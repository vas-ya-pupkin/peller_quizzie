from argparse import ArgumentParser

from app import app

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--email", dest="email", type=str)
    parser.add_argument("--password", dest="password", type=str)
    parser.add_argument("--gender", dest="gender", type=str, default='m')
    args = parser.parse_args()

    if args.email and args.password:  # если запущено с параметрами email и password, регистрируем нового админа
        from app.utils import signup
        registered = signup(
            email=args.email,
            password=args.password,
            gender=args.gender,
            is_admin=True
        )
        print(f'Register successful: {registered}')

    app.run(host='0.0.0.0', port=8000)
