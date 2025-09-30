# backend/oauth_config.py
"""
Configuration OAuth2 pour Google, GitHub, Microsoft et Facebook
À configurer avec les variables d'environnement en production
"""

import os
from typing import Dict, Any


class OAuthConfig:
    """Configuration des providers OAuth2"""
    
    # Configuration Google OAuth2
    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_OAUTH_CLIENT_ID", "")
    GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_OAUTH_CLIENT_SECRET", "")
    GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_OAUTH_REDIRECT_URI", "http://localhost:3000/oauth/callback")
    
    # Configuration GitHub OAuth2
    GITHUB_CLIENT_ID = os.getenv("GITHUB_OAUTH_CLIENT_ID", "")
    GITHUB_CLIENT_SECRET = os.getenv("GITHUB_OAUTH_CLIENT_SECRET", "")
    GITHUB_REDIRECT_URI = os.getenv("GITHUB_OAUTH_REDIRECT_URI", "http://localhost:3000/oauth/callback")
    
    # Configuration Microsoft OAuth2
    MICROSOFT_CLIENT_ID = os.getenv("MICROSOFT_OAUTH_CLIENT_ID", "")
    MICROSOFT_CLIENT_SECRET = os.getenv("MICROSOFT_OAUTH_CLIENT_SECRET", "")
    MICROSOFT_REDIRECT_URI = os.getenv("MICROSOFT_OAUTH_REDIRECT_URI", "http://localhost:3000/oauth/callback")
    
    # Configuration Facebook OAuth2
    FACEBOOK_CLIENT_ID = os.getenv("FACEBOOK_OAUTH_CLIENT_ID", "")
    FACEBOOK_CLIENT_SECRET = os.getenv("FACEBOOK_OAUTH_CLIENT_SECRET", "")
    FACEBOOK_REDIRECT_URI = os.getenv("FACEBOOK_OAUTH_REDIRECT_URI", "http://localhost:3000/oauth/callback")
    
    @classmethod
    def get_provider_config(cls, provider: str) -> Dict[str, Any]:
        """Retourne la configuration pour un provider spécifique"""
        configs = {
            "google": {
                "client_id": cls.GOOGLE_CLIENT_ID,
                "client_secret": cls.GOOGLE_CLIENT_SECRET,
                "redirect_uri": cls.GOOGLE_REDIRECT_URI,
                "authorization_url": "https://accounts.google.com/o/oauth2/v2/auth",
                "token_url": "https://oauth2.googleapis.com/token",
                "userinfo_url": "https://www.googleapis.com/oauth2/v3/userinfo",
                "scope": "openid email profile",
            },
            "github": {
                "client_id": cls.GITHUB_CLIENT_ID,
                "client_secret": cls.GITHUB_CLIENT_SECRET,
                "redirect_uri": cls.GITHUB_REDIRECT_URI,
                "authorization_url": "https://github.com/login/oauth/authorize",
                "token_url": "https://github.com/login/oauth/access_token",
                "userinfo_url": "https://api.github.com/user",
                "scope": "user:email",
            },
            "microsoft": {
                "client_id": cls.MICROSOFT_CLIENT_ID,
                "client_secret": cls.MICROSOFT_CLIENT_SECRET,
                "redirect_uri": cls.MICROSOFT_REDIRECT_URI,
                "authorization_url": "https://login.microsoftonline.com/common/oauth2/v2.0/authorize",
                "token_url": "https://login.microsoftonline.com/common/oauth2/v2.0/token",
                "userinfo_url": "https://graph.microsoft.com/v1.0/me",
                "scope": "openid email profile User.Read",
            },
            "facebook": {
                "client_id": cls.FACEBOOK_CLIENT_ID,
                "client_secret": cls.FACEBOOK_CLIENT_SECRET,
                "redirect_uri": cls.FACEBOOK_REDIRECT_URI,
                "authorization_url": "https://www.facebook.com/v12.0/dialog/oauth",
                "token_url": "https://graph.facebook.com/v12.0/oauth/access_token",
                "userinfo_url": "https://graph.facebook.com/v12.0/me",
                "scope": "email public_profile",
            }
        }
        
        return configs.get(provider, {})
    
    @classmethod
    def is_provider_enabled(cls, provider: str) -> bool:
        """Vérifie si un provider OAuth2 est configuré et activé"""
        config = cls.get_provider_config(provider)
        return bool(config.get("client_id") and config.get("client_secret"))
    
    @classmethod
    def get_enabled_providers(cls) -> list:
        """Retourne la liste des providers OAuth2 activés"""
        return [provider for provider in ["google", "github", "microsoft", "facebook"]
                if cls.is_provider_enabled(provider)]


# Instructions de configuration
OAUTH_SETUP_INSTRUCTIONS = """
🔐 CONFIGURATION OAUTH2

Pour activer l'authentification OAuth2, configurez les variables d'environnement suivantes :

1. 📧 GOOGLE OAUTH2
   - Allez sur Google Cloud Console: https://console.cloud.google.com/
   - Créez un nouveau projet ou sélectionnez un existant
   - Activez l'API Google+ 
   - Créez des identifiants OAuth 2.0
   - Ajoutez l'URI de redirection: http://localhost:3000/oauth/callback
   - Variables d'environnement :
     GOOGLE_OAUTH_CLIENT_ID=votre_client_id_google
     GOOGLE_OAUTH_CLIENT_SECRET=votre_client_secret_google

2. 🐙 GITHUB OAUTH2
   - Allez sur GitHub Settings > Developer settings > OAuth Apps
   - Créez une nouvelle OAuth App
   - Homepage URL: http://localhost:3000
   - Authorization callback URL: http://localhost:3000/oauth/callback
   - Variables d'environnement :
     GITHUB_OAUTH_CLIENT_ID=votre_client_id_github
     GITHUB_OAUTH_CLIENT_SECRET=votre_client_secret_github

3. 🪟 MICROSOFT OAUTH2
   - Allez sur Azure Portal: https://portal.azure.com/
   - Azure Active Directory > App registrations
   - Créez une nouvelle inscription d'application
   - Plateformes > Ajouter une plateforme > Web
   - URL de redirection: http://localhost:3000/oauth/callback
   - Variables d'environnement :
     MICROSOFT_OAUTH_CLIENT_ID=votre_client_id_microsoft
     MICROSOFT_OAUTH_CLIENT_SECRET=votre_client_secret_microsoft

4. 🚀 DÉMARRAGE
   - Copiez le fichier .env.example vers .env
   - Remplissez les variables OAuth2
   - Redémarrez l'application
"""


def check_oauth_configuration():
    """Vérifie la configuration OAuth2 et affiche les instructions si nécessaire"""
    enabled_providers = OAuthConfig.get_enabled_providers()
    
    if not enabled_providers:
        print("⚠️  AUCUN PROVIDER OAUTH2 CONFIGURÉ")
        print(OAUTH_SETUP_INSTRUCTIONS)
        return False
    
    print(f"✅ Providers OAuth2 activés: {', '.join(enabled_providers)}")
    return True


if __name__ == "__main__":
    check_oauth_configuration()