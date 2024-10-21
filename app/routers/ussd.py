import json
import random

from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.orm import Session as Db_session

from app.configs.database import get_db
from app.core.utils import secure_pwd
from app.models.session_model import get_session, create_session, update_session, delete_session
from app.models.user_model import get_user
from app.schemas.session_schema import SessionCreate
from app.schemas.user_schema import UserCreate
from app.schemas.ussd_schema import USSDRequestSchema, USSDResponseSchema

router = APIRouter(
    prefix="/api/v1/ussd",
    tags=["ussd"],
    responses={404: {"description": "Not found"}},
)


@router.post("", response_model=USSDResponseSchema)
async def ussd_handler(request: USSDRequestSchema, db: Db_session = Depends(get_db)):
    session_id = request.sessionid
    msisdn = request.msisdn
    user_input = request.message or ""

    session = get_session(db, session_id)

    if not session:
        data = {"phone_number": msisdn}
        session_data = SessionCreate(session_id=session_id, user_id=1, state="menu_principal", data=data)
        create_session(db, session_data)
        client = get_user(db, msisdn)

        if client:
            return USSDResponseSchema(
                message="Bienvenue sur PerfectPay\n1-Transfert\n2-Retrait\n3-Paiement services\n4-Vendre\n5-Acheter\n6-Solde\n7-Paiement\n8-Recharger",
                command="1"
            )
        return USSDResponseSchema(
            message="Bienvenue sur PerfectPay\n0-Inscription",
            command="1"
        )

    current_state = session.state
    session_data = json.loads(session.data)

    # Gestion des différents états du menu USSD
    if current_state == "menu_principal":
        if user_input == "0":
            # Inscription
            update_session(db, session_id, "inscription", session_data)
            return USSDResponseSchema(
                message="Veuillez entrer votre numéro de téléphone pour vous inscrire",
                command="1"
            )

        elif user_input == "1":
            # Transfert d'argent
            update_session(db, session_id, "transfert_numero", session_data)
            return USSDResponseSchema(
                message="Entrez le numéro du bénéficiaire",
                command="1"
            )
        elif user_input == "2":
            # Retrait
            update_session(db, session_id, "retrait_numero", session_data)
            return USSDResponseSchema(
                message="Entrez le numéro du marchand",
                command="1"
            )

        # Autres options du menu principal
        elif user_input == "6":
            # Consultation du solde
            update_session(db, session_id, "solde_pin", session_data)
            return USSDResponseSchema(
                message="Entrez votre code PIN pour consulter votre solde",
                command="1"
            )
        else:
            return USSDResponseSchema(
                message="Option invalide, réessayez.\n1. Inscription\n2. Transfert\n3. Retrait\n4. Consultation de solde",
                command="1"
            )

    elif current_state == "inscription":
        # Inscription d'un utilisateur
        phone_number = user_input
        client = get_client(db, phone_number)
        if client:
            return USSDResponseSchema(
                message=f"Le numéro {phone_number} est déjà enregistré.",
                command="0"
            )

        pin = str(random.randint(10000, 99999))
        new_client = UserCreate(phone_number=phone_number, pin=secure_pwd(pin))
        create_client(db, new_client)

        delete_session(db, session_id)

        return USSDResponseSchema(
            message=f"Inscription réussie. Votre PIN est {pin}.",
            command="0"
        )

    elif current_state == "transfert_numero":
        # Sauvegarder le numéro du bénéficiaire et passer à la saisie du montant
        session_data["beneficiary"] = user_input
        update_session(db, session_id, "transfert_montant", session_data)
        return USSDResponseSchema(
            message="Entrez le montant à transférer",
            command="1"
        )

    elif current_state == "transfert_montant":
        try:
            montant = float(user_input)
            session_data["montant"] = montant
            update_session(db, session_id, "transfert_pin", session_data)
            return USSDResponseSchema(
                message="Entrez votre code PIN pour confirmer le transfert",
                command="1"
            )
        except ValueError:
            return USSDResponseSchema(
                message="Montant invalide. Veuillez entrer un montant valide.",
                command="1"
            )

    elif current_state == "transfert_pin":
        pin = user_input
        phone_number = session_data["phone_number"]
        beneficiary = session_data["beneficiary"]
        montant = session_data["montant"]

        client = get_client(db, phone_number)
        if not client or client.pin != pin:
            delete_session(db, session_id)
            return USSDResponseSchema(
                message="Code PIN incorrect. Session terminée.",
                command="0"
            )

        if client.solde < montant:
            delete_session(db, session_id)
            return USSDResponseSchema(
                message="Solde insuffisant. Session terminée.",
                command="0"
            )

        # Vérification du bénéficiaire
        beneficiary_client = get_client(db, beneficiary)
        if not beneficiary_client:
            delete_session(db, session_id)
            return USSDResponseSchema(
                message="Numéro du bénéficiaire invalide. Session terminée.",
                command="0"
            )

        client.solde -= montant
        beneficiary_client.solde += montant
        db.commit()

        delete_session(db, session_id)
        return USSDResponseSchema(
            message=f"Transfert de {montant} FCFA à {beneficiary}. Merci d'utiliser PerfectPay.",
            command="0"
        )

    delete_session(db, session_id)
    return USSDResponseSchema(
        message="Une erreur est survenue. Session terminée.",
        command="0"
    )
