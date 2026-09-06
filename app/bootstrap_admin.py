"""Cria o primeiro administrador a partir de uma conta já cadastrada."""
import argparse
from app.database import SessionLocal
from app.models.usuario import Usuario


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("email")
    args = parser.parse_args()
    with SessionLocal() as db:
        if db.query(Usuario).filter(Usuario.tipo == "administrador").first():
            raise SystemExit("Ja existe administrador. Use o painel para promover outras contas.")
        usuario = db.query(Usuario).filter(Usuario.email == args.email).first()
        if not usuario:
            raise SystemExit("Cadastre essa conta antes de executar este comando.")
        usuario.tipo = "administrador"
        db.commit()
        print("Primeiro administrador configurado.")


if __name__ == "__main__":
    main()
