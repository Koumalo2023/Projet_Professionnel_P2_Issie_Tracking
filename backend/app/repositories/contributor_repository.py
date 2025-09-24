# api/app/repositories/contributor_repository.py
from typing import List
from sqlalchemy.orm import Session
from app.models.contributor import Contributor

class ContributorRepository:
    def add_contributor(self, db: Session, project_id: int, user_id: int) -> Contributor:
        """
        Ajoute un contributeur à un projet.
        """
        db_contributor = Contributor(project_id=project_id, user_id=user_id)
        db.add(db_contributor)
        db.commit()
        db.refresh(db_contributor)
        return db_contributor

    def get_contributors(self, db: Session, project_id: int) -> List[Contributor]:
        """
        Récupère tous les contributeurs d'un projet.
        """
        return db.query(Contributor).filter(Contributor.project_id == project_id).all()

    def remove_contributor(self, db: Session, project_id: int, user_id: int) -> None:
        """
        Supprime un contributeur d'un projet.
        """
        contributor = db.query(Contributor).filter(Contributor.project_id == project_id, Contributor.user_id == user_id).first()
        if contributor:
            db.delete(contributor)
            db.commit()