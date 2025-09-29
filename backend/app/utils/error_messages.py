# app/utils/error_messages.py
from typing import Dict, Optional


# Catalogue des codes d'erreur et leurs messages
ERROR_MESSAGES: Dict[str, str] = {
    # Catégorie Authentication (AUTH_*)
    "AUTH_INVALID_CREDENTIALS": "Identifiants invalides",
    "AUTH_TOKEN_EXPIRED": "Token expiré",
    "AUTH_TOKEN_INVALID": "Token invalide",
    "AUTH_REFRESH_TOKEN_INVALID": "Refresh token invalide",
    "AUTH_MISSING_TOKEN": "Token d'authentification manquant",
    "AUTH_INSUFFICIENT_PERMISSIONS": "Permissions d'authentification insuffisantes",
    
    # Catégorie User (USER_*)
    "USER_NOT_FOUND": "Utilisateur non trouvé",
    "USER_EMAIL_EXISTS": "Email déjà utilisé",
    "USER_USERNAME_EXISTS": "Nom d'utilisateur déjà pris",
    "USER_INACTIVE": "Compte utilisateur inactif",
    "USER_PROFILE_NOT_FOUND": "Profil utilisateur non trouvé",
    "USER_UPDATE_FORBIDDEN": "Mise à jour de l'utilisateur interdite",
    
    # Catégorie Project (PROJECT_*)
    "PROJECT_NOT_FOUND": "Projet non trouvé",
    "PROJECT_ACCESS_DENIED": "Accès au projet refusé",
    "PROJECT_ALREADY_EXISTS": "Projet déjà existant",
    "PROJECT_CREATION_FORBIDDEN": "Création de projet interdite",
    "PROJECT_UPDATE_FORBIDDEN": "Mise à jour du projet interdite",
    "PROJECT_DELETION_FORBIDDEN": "Suppression du projet interdite",
    
    # Catégorie Issue (ISSUE_*)
    "ISSUE_NOT_FOUND": "Issue non trouvée",
    "ISSUE_ACCESS_DENIED": "Accès à l'issue refusé",
    "ISSUE_ALREADY_EXISTS": "Issue déjà existante",
    "ISSUE_CREATION_FORBIDDEN": "Création d'issue interdite",
    "ISSUE_UPDATE_FORBIDDEN": "Mise à jour de l'issue interdite",
    "ISSUE_DELETION_FORBIDDEN": "Suppression de l'issue interdite",
    "ISSUE_STATUS_INVALID": "Statut de l'issue invalide",
    "ISSUE_PRIORITY_INVALID": "Priorité de l'issue invalide",
    
    # Catégorie Comment (COMMENT_*)
    "COMMENT_NOT_FOUND": "Commentaire non trouvé",
    "COMMENT_ACCESS_DENIED": "Accès au commentaire refusé",
    "COMMENT_CREATION_FORBIDDEN": "Création de commentaire interdite",
    "COMMENT_UPDATE_FORBIDDEN": "Mise à jour du commentaire interdite",
    "COMMENT_DELETION_FORBIDDEN": "Suppression du commentaire interdite",
    
    # Catégorie Contributor (CONTRIBUTOR_*)
    "CONTRIBUTOR_NOT_FOUND": "Contributeur non trouvé",
    "CONTRIBUTOR_ALREADY_EXISTS": "Contributeur déjà ajouté",
    "CONTRIBUTOR_ACCESS_DENIED": "Accès au contributeur refusé",
    "CONTRIBUTOR_ADDITION_FORBIDDEN": "Ajout de contributeur interdit",
    "CONTRIBUTOR_REMOVAL_FORBIDDEN": "Retrait de contributeur interdit",
    
    # Catégorie Validation (VALIDATION_*)
    "VALIDATION_ERROR": "Erreur de validation des données",
    "VALIDATION_REQUIRED_FIELD": "Champ obligatoire manquant",
    "VALIDATION_INVALID_FORMAT": "Format invalide",
    "VALIDATION_INVALID_EMAIL": "Format d'email invalide",
    "VALIDATION_INVALID_PASSWORD": "Format de mot de passe invalide",
    "VALIDATION_INVALID_USERNAME": "Format de nom d'utilisateur invalide",
    "VALIDATION_INVALID_DATE": "Format de date invalide",
    "VALIDATION_INVALID_NUMBER": "Format numérique invalide",
    "VALIDATION_OUT_OF_RANGE": "Valeur hors limites",
    "VALIDATION_UNIQUE_CONSTRAINT": "Violation de contrainte d'unicité",
    
    # Catégorie Database (DATABASE_*)
    "DATABASE_ERROR": "Erreur de base de données",
    "DATABASE_CONNECTION_ERROR": "Erreur de connexion à la base de données",
    "DATABASE_QUERY_ERROR": "Erreur lors de l'exécution de la requête",
    "DATABASE_CONSTRAINT_VIOLATION": "Violation de contrainte de base de données",
    "DATABASE_TIMEOUT": "Timeout de la base de données",
    
    # Catégorie Network (NETWORK_*)
    "NETWORK_ERROR": "Erreur de réseau",
    "NETWORK_TIMEOUT": "Timeout réseau",
    "NETWORK_CONNECTION_REFUSED": "Connexion réseau refusée",
    "NETWORK_HOST_UNREACHABLE": "Hôte réseau inaccessible",
    
    # Catégorie Server (SERVER_*)
    "INTERNAL_SERVER_ERROR": "Erreur interne du serveur",
    "SERVICE_UNAVAILABLE": "Service indisponible",
    "RATE_LIMIT_EXCEEDED": "Limite de requêtes dépassée",
    "MAINTENANCE_MODE": "Mode maintenance activé",
    
    # Catégorie File (FILE_*)
    "FILE_NOT_FOUND": "Fichier non trouvé",
    "FILE_ACCESS_DENIED": "Accès au fichier refusé",
    "FILE_UPLOAD_ERROR": "Erreur lors du téléchargement du fichier",
    "FILE_SIZE_EXCEEDED": "Taille du fichier dépassée",
    "FILE_FORMAT_UNSUPPORTED": "Format de fichier non supporté",
    
    # Catégorie Generic (GENERIC_*)
    "NOT_FOUND": "Ressource non trouvée",
    "UNAUTHORIZED": "Non autorisé",
    "FORBIDDEN": "Accès interdit",
    "BAD_REQUEST": "Requête invalide",
    "CONFLICT": "Conflit détecté",
    "PRECONDITION_FAILED": "Précondition échouée",
    "UNPROCESSABLE_ENTITY": "Entité non traitable",
    "TOO_MANY_REQUESTS": "Trop de requêtes",
}


def get_error_message(code: str, details: Optional[str] = None) -> dict:
    """
    Retourne un message d'erreur standardisé
    """
    return {
        "code": code,
        "message": ERROR_MESSAGES.get(code, "Erreur inconnue"),
        "details": details
    }


def format_validation_error(field: str, error_type: str, details: Optional[str] = None) -> dict:
    """
    Formate une erreur de validation spécifique
    """
    code = f"VALIDATION_{error_type.upper()}"
    message = ERROR_MESSAGES.get(code, "Erreur de validation")
    
    if details:
        message = f"{message} : {details}"
    
    return {
        "code": code,
        "message": message,
        "field": field,
        "details": details
    }


# Mapping des codes HTTP vers les codes d'erreur métier
HTTP_ERROR_MAPPING = {
    400: "BAD_REQUEST",
    401: "UNAUTHORIZED",
    403: "FORBIDDEN",
    404: "NOT_FOUND",
    409: "CONFLICT",
    422: "VALIDATION_ERROR",
    429: "RATE_LIMIT_EXCEEDED",
    500: "INTERNAL_SERVER_ERROR",
    503: "SERVICE_UNAVAILABLE",
}


def get_error_code_from_http_status(status_code: int) -> str:
    """
    Retourne le code d'erreur métier correspondant au code HTTP
    """
    return HTTP_ERROR_MAPPING.get(status_code, "INTERNAL_SERVER_ERROR")
