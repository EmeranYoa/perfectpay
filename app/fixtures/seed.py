import random
from faker import Faker
from sqlalchemy.orm import Session
from app.models.user_model import CurrencyRate, User, Wallet, CurrencyRate
from app.models.roles_model import Merchant, Partner, Client, Admin
from app.core.utils import secure_pwd, generate_pin_code, generate_merchant_code

faker = Faker()

def seed_database(db: Session):
    """
    Seed the database with fake data using Faker.
    Args:
        db (Session): SQLAlchemy session.
        count (int): Number of users to generate.
    """
    
    _seed_user(db, count=1000)
    print("Database seeded successfully with Faker.")


def _seed_user(db: Session, count: int = 10, default_pin: str = "14982", default_passwd: str = "Password1234"):
    """
    Seed the database with fake data using Faker.
    Args:
        db (Session): SQLAlchemy session.
        count (int): Number of users to generate.
        default_pin (str): Default PIN code.
        default_passwd (str): Default password.
    """
    
    # create admin user
    fake_phone_number = _generate_phone_number()
    fake_pin = secure_pwd(default_pin)
    fake_username = faker.user_name()
    fake_email = faker.email()
    fake_password = secure_pwd(default_passwd)
    fake_first_name = faker.first_name()
    fake_last_name = faker.last_name()
    fake_date_of_birth = faker.date_of_birth(minimum_age=18, maximum_age=60)
    fake_place_of_birth = faker.city()

    user = User(
        phone_number=fake_phone_number,
        pin=fake_pin,
        username=fake_username,
        email=fake_email,
        password=fake_password,
        first_name=fake_first_name,
        last_name=fake_last_name,
        date_of_birth=fake_date_of_birth,
        place_of_birth=fake_place_of_birth,
    )
    db.add(user)
    db.commit()

    currency = "USD"
    if user.phone_number.startswith("+237"):
        currency = "XAF"
    if user.phone_number.startswith("+33"):
        currency = "EUR"


    wallet = Wallet(owner_id=user.id, balance=random.uniform(0, 1000), currency=currency)
    db.add(wallet)

    admin = Admin(owner_id=user.id)
    db.add(admin)
    
    print(f"Seeding {count} users...")
    roles = ["client", "merchant", "partner"]
    
    for _ in range(count):
        fake_phone_number = _generate_phone_number()
        fake_pin = secure_pwd(default_pin)
        fake_username = faker.user_name()
        fake_email = faker.email()
        fake_password = secure_pwd(default_passwd)
        fake_first_name = faker.first_name()
        fake_last_name = faker.last_name()
        fake_date_of_birth = faker.date_of_birth(minimum_age=18, maximum_age=60)
        fake_place_of_birth = faker.city()
        fake_role = random.choice(roles)

        if db.query(User).filter(
            (User.phone_number == fake_phone_number) | (User.email == fake_email)
        ).first():
            continue

        user = User(
            phone_number=fake_phone_number,
            pin=fake_pin,
            username=fake_username,
            email=fake_email,
            password=fake_password,
            first_name=fake_first_name,
            last_name=fake_last_name,
            date_of_birth=fake_date_of_birth,
            place_of_birth=fake_place_of_birth,
        )
        db.add(user)
        db.commit()

        currency = "USD"
        if user.phone_number.startswith("+237"):
            currency = "XAF"
        if user.phone_number.startswith("+33"):
            currency = "EUR"


        wallet = Wallet(owner_id=user.id, balance=random.uniform(0, 1000), currency=currency)
        db.add(wallet)

        if fake_role == "client":
            client = Client(owner_id=user.id, registered_by=None)
            db.add(client)
            db.commit()
        elif fake_role == "merchant":
            merchant_email = faker.email()
            # check if the email already exists in the database
            while db.query(Merchant).filter(Merchant.email == merchant_email).first():
                merchant_email = faker.email()

            business_name = faker.company()
            # check if the business name already exists in the database
            while db.query(Merchant).filter(Merchant.business_name == business_name).first():
                business_name = faker.company()

            merchant = Merchant(owner_id=user.id, business_name=business_name, merchant_code=generate_merchant_code(), phone_number=_generate_phone_number(), email=merchant_email, registered_by=None)
            db.add(merchant)
            db.commit()
        elif fake_role == "partner":
            partner_email = faker.email()
            # check if the email already exists in the database
            if db.query(Partner).filter(Partner.email == partner_email).first():
                partner_email = faker.email()
            
            partner = Partner(owner_id=user.id, partner_code=generate_merchant_code(), phone_number=_generate_phone_number(), email=partner_email)
            db.add(partner)

            db.commit()

    print(f"{count} users seeded successfully.")

def _generate_phone_number():
    """
    Generate a phone number with specific country codes: +237, +1, or +33.
    """
    country_code = random.choice(["+237", "+1", "+33"])
    local_number = faker.numerify("#########")
    return f"{country_code}{local_number}"
