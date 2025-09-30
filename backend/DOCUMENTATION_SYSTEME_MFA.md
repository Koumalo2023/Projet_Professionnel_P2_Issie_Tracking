# Documentation - Système d'Authentification Multi-Facteurs (MFA)

## Table des Matières
1. [Aperçu du Système](#aperçu-du-système)
2. [Architecture Technique](#architecture-technique)
3. [Modèles de Données](#modèles-de-données)
4. [API Endpoints](#api-endpoints)
5. [Workflow de Configuration](#workflow-de-configuration)
6. [Intégration avec l'Authentification](#intégration-avec-lauthentification)
7. [Sécurité et Bonnes Pratiques](#sécurité-et-bonnes-pratiques)
8. [Tests et Validation](#tests-et-validation)
9. [Dépannage](#dépannage)

## Aperçu du Système

Le système d'authentification multi-facteurs (MFA) fournit une couche de sécurité supplémentaire pour protéger les comptes utilisateurs contre les accès non autorisés. Il implémente le standard TOTP (Time-based One-Time Password) compatible avec les applications d'authentification comme Google Authenticator, Authy, Microsoft Authenticator, etc.

### Fonctionnalités Principales

- ✅ **Configuration MFA** : Génération de clés secrètes et QR codes
- ✅ **Vérification TOTP** : Validation des codes à 6 chiffres basés sur le temps
- ✅ **Codes de récupération** : Codes d'urgence pour les situations de perte d'accès
- ✅ **Gestion des sessions** : Suivi des tentatives de connexion
- ✅ **Statistiques et monitoring** : Métriques d'utilisation et de sécurité
- ✅ **Désactivation sécurisée** : Processus de désactivation avec vérification

## Architecture Technique

### Composants du Système

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  Contrôleur     │◄──►│  Service MFA     │◄──►│  Base de       │
│      MFA        │    │                  │    │  Données       │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Schémas       │    │    Modèles       │    │  Algorithmes    │
│   Pydantic      │    │    SQLAlchemy    │    │    TOTP         │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

### Fichiers Implémentés

- [`backend/app/models/mfa.py`](backend/app/models/mfa.py) - Modèles de données MFA
- [`backend/app/services/mfa_service.py`](backend/app/services/mfa_service.py) - Service de gestion MFA
- [`backend/app/controllers/mfa_controller.py`](backend/app/controllers/mfa_controller.py) - Endpoints API MFA
- [`backend/app/schemas/mfa_schema.py`](backend/app/schemas/mfa_schema.py) - Schémas de validation
- [`backend/app/exceptions/mfa_exceptions.py`](backend/app/exceptions/mfa_exceptions.py) - Exceptions MFA
- [`backend/tests/test_mfa_controller.py`](backend/tests/test_mfa_controller.py) - Tests unitaires

## Modèles de Données

### MFASettings - Paramètres MFA

```python
class MFASettings(Base):
    __tablename__ = "mfa_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    is_enabled = Column(Boolean, default=False, nullable=False)
    method = Column(String(20), default="totp", nullable=False)  # totp, sms, email
    secret_key = Column(String(32), nullable=True)  # Clé secrète pour TOTP
    backup_codes = Column(Text, nullable=True)  # Codes de secours JSON
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
```

### MFALoginAttempt - Tentatives de Connexion

```python
class MFALoginAttempt(Base):
    __tablename__ = "mfa_login_attempts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    attempt_type = Column(String(20), nullable=False)  # setup, login, recovery
    ip_address = Column(String(45), nullable=False)
    user_agent = Column(Text, nullable=True)
    success = Column(Boolean, default=False, nullable=False)
    failure_reason = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
```

### MFARecoveryCode - Codes de Récupération

```python
class MFARecoveryCode(Base):
    __tablename__ = "mfa_recovery_codes"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    code_hash = Column(String(128), nullable=False)  # Code hashé pour sécurité
    is_used = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    used_at = Column(DateTime(timezone=True), nullable=True)
```

## API Endpoints

### Configuration MFA

#### POST /api/mfa/setup
Démarre la configuration MFA.

**Requête:**
```json
{
    "method": "totp"
}
```

**Réponse:**
```json
{
    "secret_key": "JBSWY3DPEHPK3PXP",
    "backup_codes": ["ABCD1234", "EFGH5678", ...],
    "method": "totp",
    "qr_code_url": "otpauth://totp/IssieTracking:username?..."
}
```

#### POST /api/mfa/verify
Vérifie le code MFA lors de la configuration.

**Requête:**
```json
{
    "code": "123456"
}
```

**Réponse:**
```json
{
    "success": true,
    "message": "MFA configuré et activé avec succès"
}
```

### Gestion MFA

#### GET /api/mfa/status
Récupère le statut MFA de l'utilisateur.

**Réponse:**
```json
{
    "is_enabled": true,
    "is_setup": true,
    "method": "totp",
    "setup_required": false
}
```

#### POST /api/mfa/enable
Active le MFA après vérification.

**Requête:**
```json
{
    "code": "123456"
}
```

#### POST /api/mfa/disable
Désactive le MFA.

**Requête:**
```json
{
    "password": "motdepasse"
}
```

### Codes de Récupération

#### POST /api/mfa/recovery-codes/generate
Génère de nouveaux codes de récupération.

**Réponse:**
```json
{
    "recovery_codes": ["NEWCODE1", "NEWCODE2", ...],
    "message": "Nouveaux codes de récupération générés..."
}
```

#### POST /api/mfa/recovery/verify
Vérifie un code de récupération.

**Requête:**
```json
{
    "code": "RECOVERY1"
}
```

### Monitoring et Statistiques

#### GET /api/mfa/settings
Récupère les paramètres MFA.

#### GET /api/mfa/attempts
Récupère les tentatives de connexion.

#### GET /api/mfa/stats
Récupère les statistiques MFA (administrateurs).

## Workflow de Configuration

### 1. Initialisation de la Configuration

```python
# Étape 1: Démarrer la configuration
response = client.post("/api/mfa/setup", json={"method": "totp"})
data = response.json()

secret_key = data["secret_key"]
backup_codes = data["backup_codes"]
qr_code_url = data["qr_code_url"]
```

### 2. Scan du QR Code

L'utilisateur scanne le QR code avec son application d'authentification:

```
Format du QR code:
otpauth://totp/IssieTracking:username?secret=JBSWY3DPEHPK3PXP&issuer=IssieTracking
```

### 3. Vérification du Code

```python
# Étape 2: Vérifier le code généré par l'application
response = client.post("/api/mfa/verify", json={"code": "123456"})

if response.json()["success"]:
    print("MFA activé avec succès")
else:
    print("Code invalide")
```

### 4. Sauvegarde des Codes de Récupération

```python
# IMPORTANT: Sauvegarder les codes de récupération
print("Codes de récupération à sauvegarder:")
for code in backup_codes:
    print(f"- {code}")
```

## Intégration avec l'Authentification

### Processus de Connexion avec MFA

```python
def login_with_mfa(username: str, password: str, mfa_code: str = None):
    # 1. Vérifier le nom d'utilisateur et le mot de passe
    user = authenticate_user(username, password)
    
    # 2. Vérifier si le MFA est activé
    if user.mfa_settings and user.mfa_settings.is_enabled:
        if not mfa_code:
            # Retourner que la vérification MFA est requise
            return {
                "requires_mfa": True,
                "user_id": user.id
            }
        
        # 3. Vérifier le code MFA
        if not verify_mfa_code(user, mfa_code):
            raise MFAInvalidCodeException()
    
    # 4. Générer le token d'accès
    access_token = create_access_token(data={"sub": user.id})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "requires_mfa": False
    }
```

### Middleware de Vérification MFA

Le système intègre un middleware qui peut être utilisé pour protéger les routes sensibles:

```python
@router.get("/sensitive-data")
async def get_sensitive_data(
    current_user: User = Depends(get_current_user),
    mfa_verified: bool = Depends(require_mfa_verification)
):
    # Cette route nécessite une vérification MFA récente
    return {"data": "Informations sensibles"}
```

## Sécurité et Bonnes Pratiques

### Génération Sécurisée des Clés

```python
def generate_secret_key(self) -> str:
    """Génère une clé secrète pour TOTP"""
    # Génère 20 bytes aléatoires (recommandé par RFC 6238)
    secret_bytes = secrets.token_bytes(20)
    # Encode en base32 (sans padding pour compatibilité)
    secret_key = base64.b32encode(secret_bytes).decode('utf-8').rstrip('=')
    return secret_key
```

### Validation TOTP avec Fenêtre de Temps

```python
def verify_totp_code(self, secret_key: str, code: str, window: int = 1) -> bool:
    """Vérifie un code TOTP avec une fenêtre de temps"""
    current_time = int(time.time() // 30)
    
    # Vérifie dans la fenêtre de temps (passé et futur)
    for i in range(-window, window + 1):
        expected_code = self._generate_totp_code(secret_key, current_time + i)
        if hmac.compare_digest(code, expected_code):
            return True
    
    return False
```

### Stockage Sécurisé des Codes de Récupération

```python
def hash_backup_code(self, code: str) -> str:
    """Hash un code de secours pour le stockage sécurisé"""
    return hashlib.sha256(code.encode()).hexdigest()
```

### Journalisation des Tentatives

```python
def _log_mfa_attempt(self, user_id: int, attempt_type: str, ip_address: str, 
                    reason: str, success: bool) -> None:
    """Log une tentative MFA pour le suivi de sécurité"""
    attempt = MFALoginAttempt(
        user_id=user_id,
        attempt_type=attempt_type,
        ip_address=ip_address,
        success=success,
        failure_reason=reason if not success else None
    )
    self.db.add(attempt)
    self.db.commit()
```

## Tests et Validation

### Tests Unitaires

Le système inclut des tests complets couvrant:

- Configuration et activation MFA
- Vérification des codes TOTP
- Gestion des codes de récupération
- Gestion des erreurs et exceptions
- Workflow complet d'intégration

**Exécution des tests:**
```bash
cd backend
pytest tests/test_mfa_controller.py -v
```

### Scénarios de Test Couverts

1. **Configuration MFA réussie**
2. **Configuration MFA déjà activée**
3. **Vérification de code valide/invalide**
4. **Utilisation de codes de récupération**
5. **Désactivation sécurisée**
6. **Récupération des statistiques**

## Dépannage

### Problèmes Courants et Solutions

#### 1. Désynchronisation Temporelle

**Symptôme:** Les codes TOTP ne fonctionnent pas même s'ils semblent corrects.

**Solution:**
- Vérifier la synchronisation horaire du serveur
- Ajuster la fenêtre de validation (`window` parameter)
- Utiliser `ntpdate` pour synchroniser l'heure

```python
# Augmenter la fenêtre de validation
mfa_service.verify_totp_code(secret_key, code, window=2)
```

#### 2. Perte d'Accès à l'Application d'Authentification

**Symptôme:** L'utilisateur ne peut pas générer de codes TOTP.

**Solution:**
- Utiliser les codes de récupération sauvegardés
- Processus de réinitialisation MFA (à implémenter)
- Contact avec le support administrateur

#### 3. Codes de Récupération Épuisés

**Symptôme:** Tous les codes de récupération ont été utilisés.

**Solution:**
- Générer de nouveaux codes de récupération
- Réinitialiser complètement le MFA

```python
# Générer de nouveaux codes
response = client.post("/api/mfa/recovery-codes/generate")
```

### Monitoring et Alertes

#### Métriques à Surveiller

- **Taux d'échec MFA**: Pourcentage de tentatives échouées
- **Utilisation des codes de récupération**: Fréquence d'utilisation
- **Tentatives suspectes**: IPs avec taux d'échec élevé
- **Adoption MFA**: Pourcentage d'utilisateurs avec MFA activé

#### Configuration des Alertes

```python
# Exemple d'alerte pour taux d'échec élevé
def check_mfa_failure_rate():
    recent_failures = count_recent_failed_attempts(hours=1)
    recent_total = count_recent_attempts(hours=1)
    
    if recent_total > 0:
        failure_rate = recent_failures / recent_total
        if failure_rate > 0.1:  # 10% de taux d'échec
            send_alert("Taux d'échec MFA élevé détecté")
```

## Configuration et Déploiement

### Variables d'Environnement

```python
# Configuration MFA
MFA_REQUIRED_FOR_ADMIN = True
MFA_DEFAULT_METHOD = "totp"
MFA_BACKUP_CODE_COUNT = 10
MFA_TOTP_WINDOW = 1  # Fenêtre de validation en pas de 30 secondes
```

### Migration de Base de Données

```bash
# Générer les migrations
alembic revision --autogenerate -m "Add MFA system"

# Appliquer les migrations
alembic upgrade head
```

### Intégration avec le Frontend

#### Exemple d'Intégration React

```javascript
import React, { useState } from 'react';

const MFAConfiguration = () => {
    const [step, setStep] = useState('setup');
    const [secretKey, setSecretKey] = useState('');
    const [backupCodes, setBackupCodes] = useState([]);
    const [qrCodeUrl, setQrCodeUrl] = useState('');

    const startMFASetup = async () => {
        const response = await fetch('/api/mfa/setup', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${userToken}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ method: 'totp' })
        });
        
        const data = await response.json();
        setSecretKey(data.secret_key);
        setBackupCodes(data.backup_codes);
        setQrCodeUrl(data.qr_code_url);
        setStep('verify');
    };

    const verifyMFACode = async (code) => {
        const response = await fetch('/api/mfa/verify', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${userToken}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ code })
        });
        
        const result = await response.json();
        if (result.success) {
            setStep('completed');
        } else {
            alert('Code invalide. Veuillez réessayer.');
        }
    };

    return (
        <div className="mfa-configuration">
            {step === 'setup' && (
                <button onClick={startMFASetup}>
                    Configurer l'authentification à deux facteurs
                </button>
            )}
            
            {step === 'verify' && (
                <div>
                    <img src={qrCodeUrl} alt="QR Code MFA" />
                    <p>Scannez ce QR code avec votre application d'authentification</p>
                    <input 
                        type="text" 
                        placeholder="Entrez le code à 6 chiffres"
                        onChange={(e) => verifyMFACode(e.target.value)}
                    />
                </div>
            )}
            
            {step === 'completed' && (
                <div>
                    <h3>MFA configuré avec succès!</h3>
                    <p>Sauvegardez ces codes de récupération:</p>
                    <ul>
                        {backupCodes.map((code, index) => (
                            <li key={index}>{code}</li>
                        ))}
                    </ul>
                </div>
            )}
        </div>
    );
};
```

## Conclusion

Le système MFA fournit une solution complète et sécurisée pour l'authentification multi-facteurs avec:

- ✅ **Implémentation TOTP standard** compatible avec les applications populaires
- ✅ **Gestion sécurisée** des clés et codes de récupération
- ✅ **Monitoring complet** des tentatives et statistiques
- ✅ **API RESTful** bien documentée
- ✅ **Tests complets** garantissant la fiabilité
- ✅ **Intégration transparente** avec le système d'authentification existant

Ce système améliore significativement la sécurité des comptes utilisateurs tout en maintenant une expérience utilisateur fluide et intuitive.