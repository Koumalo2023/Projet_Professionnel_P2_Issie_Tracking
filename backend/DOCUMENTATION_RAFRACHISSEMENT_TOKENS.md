# Documentation - Rafraîchissement Automatique des Tokens avec Rotation Sécurisée

## Table des Matières
1. [Aperçu du Système](#aperçu-du-système)
2. [Architecture Technique](#architecture-technique)
3. [Flux de Rafraîchissement](#flux-de-rafraîchissement)
4. [Sécurité et Rotation](#sécurité-et-rotation)
5. [API Endpoints](#api-endpoints)
6. [Configuration](#configuration)
7. [Intégration Frontend](#intégration-frontend)
8. [Tests et Monitoring](#tests-et-monitoring)

## Aperçu du Système

Le système de rafraîchissement automatique des tokens implémente une stratégie de sécurité avancée pour gérer le cycle de vie des tokens JWT avec rotation sécurisée.

### Fonctionnalités Principales

- ✅ **Rafraîchissement automatique** des tokens avant expiration
- ✅ **Rotation sécurisée** des tokens de rafraîchissement
- ✅ **Gestion multi-sessions** avec limites configurées
- ✅ **Protection contre la réutilisation** des tokens
- ✅ **Nettoyage automatique** des tokens expirés
- ✅ **Métriques et monitoring** en temps réel

## Architecture Technique

### Composants du Système

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Middleware    │◄──►│  Token Service   │◄──►│  Base de       │
│   Auto-Refresh  │    │                  │    │  Données       │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │
         ▼                       ▼
┌─────────────────┐    ┌──────────────────┐
│   Contrôleur    │    │     Schémas      │
│     Tokens      │    │   Pydantic       │
└─────────────────┘    └──────────────────┘
```

### Fichiers Implémentés

- [`backend/app/services/token_service.py`](backend/app/services/token_service.py) - Service principal de gestion des tokens
- [`backend/app/controllers/token_controller.py`](backend/app/controllers/token_controller.py) - Endpoints API pour les tokens
- [`backend/app/schemas/token_schema.py`](backend/app/schemas/token_schema.py) - Schémas Pydantic pour la validation
- [`backend/app/middleware/token_refresh_middleware.py`](backend/app/middleware/token_refresh_middleware.py) - Middleware de rafraîchissement automatique

## Flux de Rafraîchissement

### 1. Rafraîchissement Manuel

```python
# Requête de rafraîchissement
POST /api/tokens/refresh
{
    "refresh_token": "rf_1_123_abc...",
    "ip_address": "192.168.1.100",
    "user_agent": "Mozilla/5.0..."
}

# Réponse
{
    "access_token": "eyJ0eXAiOiJKV1QiLC...",
    "refresh_token": "rf_1_123_def...",
    "token_type": "bearer",
    "expires_in": 900,
    "session_id": 123
}
```

### 2. Rafraîchissement Automatique

Le middleware intercepte les requêtes et rafraîchit automatiquement les tokens :

- **Seuil de rafraîchissement** : 5 minutes avant expiration
- **Headers de réponse** : Nouveaux tokens dans les headers
- **Transparence** : L'utilisateur ne s'aperçoit pas du rafraîchissement

## Sécurité et Rotation

### Stratégie de Rotation

```python
# Ancien token de rafraîchissement
rf_1_123_abc123def456...

# Nouveau token après rotation  
rf_1_123_ghi789jkl012...
```

### Mesures de Sécurité

1. **Rotation Obligatoire** : Chaque rafraîchissement génère un nouveau token
2. **Invalidation Ancien Token** : L'ancien token devient immédiatement invalide
3. **Limite de Sessions** : Maximum 5 sessions actives par utilisateur
4. **Protection CSRF** : Intégration avec le système de sessions
5. **Journalisation** : Toutes les opérations sont journalisées

### Durées de Vie des Tokens

| Type de Token | Durée | Justification |
|---------------|-------|---------------|
| Access Token | 15 minutes | Équilibre sécurité et utilisabilité |
| Refresh Token | 7 jours | Session utilisateur prolongée |
| Session | 30 jours | Persistance des préférences |

## API Endpoints

### POST /api/tokens/refresh
Rafraîchit les tokens avec rotation sécurisée.

**Body:**
```json
{
    "refresh_token": "string",
    "ip_address": "string (optionnel)",
    "user_agent": "string (optionnel)"
}
```

**Réponse:**
```json
{
    "access_token": "string",
    "refresh_token": "string", 
    "token_type": "bearer",
    "expires_in": 900,
    "session_id": 123
}
```

### POST /api/tokens/revoke
Révoque des tokens spécifiques ou toutes les sessions.

**Body:**
```json
{
    "session_id": 123,
    "revoke_all": false
}
```

### GET /api/tokens/metrics
Retourne les métriques des tokens pour l'utilisateur.

**Réponse:**
```json
{
    "active_sessions": 2,
    "soon_expiring_sessions": 1,
    "max_allowed_sessions": 5,
    "access_token_duration_minutes": 15,
    "refresh_token_duration_days": 7,
    "can_create_new_session": true
}
```

### POST /api/tokens/cleanup
Nettoie les tokens expirés (administration).

### POST /api/tokens/validate
Valide un token et retourne ses informations.

### GET /api/tokens/config
Retourne la configuration actuelle.

### GET /api/tokens/health
Vérification de santé du service.

## Configuration

### Variables de Configuration

```python
class TokenService:
    # Durée de vie des tokens
    access_token_expire_minutes = 15
    refresh_token_expire_days = 7
    
    # Limites de sécurité
    max_refresh_tokens_per_user = 5
    
    # Seuil de rafraîchissement automatique
    refresh_threshold_seconds = 300  # 5 minutes
    
    # Configuration JWT
    jwt_secret_key = "your-secret-key-change-in-production"
    jwt_algorithm = "HS256"
```

### Intégration dans l'Application

Le système est intégré dans [`backend/app/main.py`](backend/app/main.py) :

```python
# Import du contrôleur
from app.controllers.token_controller import router as token_router

# Intégration du middleware
from app.middleware.token_refresh_middleware import token_refresh_middleware
app.middleware("http")(token_refresh_middleware)

# Inclusion du routeur
app.include_router(token_router, prefix="/api")
```

## Intégration Frontend

### Gestion des Tokens côté Client

```javascript
class TokenManager {
    constructor() {
        this.accessToken = localStorage.getItem('access_token');
        this.refreshToken = localStorage.getItem('refresh_token');
        this.refreshInProgress = false;
    }
    
    // Rafraîchissement automatique
    async refreshTokens() {
        if (this.refreshInProgress) return;
        
        this.refreshInProgress = true;
        
        try {
            const response = await fetch('/api/tokens/refresh', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Refresh-Token': this.refreshToken
                },
                body: JSON.stringify({
                    refresh_token: this.refreshToken
                })
            });
            
            if (response.ok) {
                const data = await response.json();
                this.updateTokens(data);
            }
        } catch (error) {
            console.error('Erreur de rafraîchissement:', error);
        } finally {
            this.refreshInProgress = false;
        }
    }
    
    // Gestion des réponses avec nouveaux tokens
    handleResponse(response) {
        const newAccessToken = response.headers.get('X-New-Access-Token');
        const newRefreshToken = response.headers.get('X-New-Refresh-Token');
        
        if (newAccessToken && newRefreshToken) {
            this.updateTokens({
                access_token: newAccessToken,
                refresh_token: newRefreshToken
            });
        }
        
        return response;
    }
}
```

### Interceptor Axios/Fetch

```javascript
// Interceptor pour le rafraîchissement automatique
axios.interceptors.response.use(
    response => {
        // Vérifie les nouveaux tokens dans les headers
        const newAccessToken = response.headers['x-new-access-token'];
        const newRefreshToken = response.headers['x-new-refresh-token'];
        
        if (newAccessToken && newRefreshToken) {
            tokenManager.updateTokens({
                access_token: newAccessToken,
                refresh_token: newRefreshToken
            });
        }
        
        return response;
    },
    async error => {
        if (error.response?.status === 401) {
            // Tentative de rafraîchissement
            await tokenManager.refreshTokens();
            // Retente la requête originale
            return axios(error.config);
        }
        return Promise.reject(error);
    }
);
```

## Tests et Monitoring

### Tests du Service

```python
def test_token_refresh_rotation():
    """Test la rotation sécurisée des tokens"""
    # Création initiale des tokens
    access_token, refresh_token = token_service.create_tokens(user, session)
    
    # Premier rafraîchissement
    new_access, new_refresh, session = token_service.refresh_tokens(refresh_token)
    
    # Vérifie que les nouveaux tokens sont différents
    assert access_token != new_access
    assert refresh_token != new_refresh
    
    # Vérifie que l'ancien token est invalidé
    with pytest.raises(TokenRevokedException):
        token_service.refresh_tokens(refresh_token)
```

### Métriques de Monitoring

- **Taux de rafraîchissement** : Pourcentage de requêtes avec rafraîchissement automatique
- **Échecs de rafraîchissement** : Nombre d'échecs de rafraîchissement automatique
- **Sessions actives** : Nombre de sessions actives par utilisateur
- **Tokens expirés nettoyés** : Statistiques de nettoyage automatique

### Logs de Sécurité

```python
# Journalisation des opérations critiques
logger.info(f"Tokens créés pour l'utilisateur {user.id}, session {session.id}")
logger.info(f"Tokens rafraîchis pour l'utilisateur {user.id}, session {session.id}") 
logger.info(f"Tokens révoqués pour la session {session_id}")
logger.info(f"Nettoyage des tokens: {stats}")
```

## Meilleures Pratiques

### Sécurité

1. **Stockage Sécurisé** : Tokens dans localStorage avec httpOnly cookies pour le refresh
2. **Rotation Obligatoire** : Toujours générer de nouveaux tokens lors du rafraîchissement
3. **Limitation de Sessions** : Empêcher la création de sessions illimitées
4. **Validation côté Serveur** : Toujours valider les tokens côté serveur

### Performance

1. **Cache des Tokens** : Mettre en cache les validations de tokens fréquentes
2. **Nettoyage Asynchrone** : Exécuter le nettoyage des tokens en arrière-plan
3. **Compression des Payloads** : Minimiser la taille des tokens JWT

### Maintenance

1. **Configuration Externalisée** : Variables d'environnement pour les durées
2. **Monitoring Continu** : Surveiller les métriques de performance et sécurité
3. **Tests Réguliers** : Tester régulièrement les scénarios d'expiration et rafraîchissement

## Conclusion

Le système de rafraîchissement automatique des tokens avec rotation sécurisée fournit :

- ✅ **Expérience utilisateur transparente** avec rafraîchissement automatique
- ✅ **Sécurité renforcée** avec rotation obligatoire des tokens
- ✅ **Scalabilité** avec gestion multi-sessions
- ✅ **Maintenabilité** avec architecture modulaire
- ✅ **Monitoring complet** avec métriques et journalisation

Ce système s'intègre parfaitement avec l'architecture existante RBAC, OAuth2, et gestion des sessions pour fournir une solution d'authentification complète et sécurisée.