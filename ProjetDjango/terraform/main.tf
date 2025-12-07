# 1. BLOC TERRAFORM : prérequis
terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm" 
      version = "~> 3.0"
    }
  }
}

# 2. PROVIDER : configuration connexion à Azure
provider "azurerm" {
  features {} 
  # L'authentification se fait via 'az login' mis deja en termianl
}

# 3. VARIABLES : Pour rendre le code flexible
variable "prefix" {
  default     = "projetazure" 
  description = "Préfixe pour nommer toutes les ressources"
}

variable "location" {
  default     = "Switzerland North" 
  description = "Région Azure où déployer"
}

variable "django_secret_key" {
  type        = string
  description = "Clé secrète Django pour la prod"
  sensitive   = true # Important : masque la clé dans les logs
}

# 4. RESOURCE GROUP : Le dossier logique qui contient tout
resource "azurerm_resource_group" "rg" {
  name     = "${var.prefix}-rg"
  location = var.location
}

# 5. AZURE CONTAINER REGISTRY (ACR) : garage à images Docker

resource "azurerm_container_registry" "acr" {
  name                = "${var.prefix}acr" 
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  sku                 = "Basic"            
  admin_enabled       = true               
}

# 6. STORAGE ACCOUNT : disque dur pour fichiers media
resource "azurerm_storage_account" "sa" {
  name                     = "${var.prefix}store99"
  resource_group_name      = azurerm_resource_group.rg.name
  location                 = azurerm_resource_group.rg.location
  account_tier             = "Standard"
  account_replication_type = "LRS" 
}

# 7. CONTENEUR DE STOCKAGE : Le dossier virtuel "media" dans le Storage
resource "azurerm_storage_container" "media" {
  name                  = "media"
  storage_account_name  = azurerm_storage_account.sa.name
  container_access_type = "blob" 
}

# 8. APP SERVICE PLAN : Le serveur (l'ordinateur) qui fait tourner l'app
resource "azurerm_service_plan" "plan" {
  name                = "${var.prefix}-plan"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  os_type             = "Linux" 
  sku_name            = "B1"   
}

# 9. WEB APP FOR CONTAINERS : L'application elle-même
resource "azurerm_linux_web_app" "webapp" {
  name                = "${var.prefix}-webapp" # URL : [projetazure]-webapp.azurewebsites.net
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  service_plan_id     = azurerm_service_plan.plan.id

  site_config {
    application_stack {
      # image de démarrage
      docker_image_name   = "${azurerm_container_registry.acr.login_server}/monapp:latest"
      docker_registry_url = "https://${azurerm_container_registry.acr.login_server}"
      # Récupération automatique des identifiants de l'ACR créé plus haut
      docker_registry_username = azurerm_container_registry.acr.admin_username
      docker_registry_password = azurerm_container_registry.acr.admin_password
    }
  }


  app_settings = {
    # Connexion au stockage
    "AZURE_STORAGE_CONNECTION_STRING" = azurerm_storage_account.sa.primary_connection_string
    "AZURE_ACCOUNT_NAME"              = azurerm_storage_account.sa.name
    "AZURE_CUSTOM_DOMAIN"             = "${azurerm_storage_account.sa.name}.blob.core.windows.net"
    
    # Sécurité Django
    "SECRET_KEY"                      = var.django_secret_key
    "DEBUG"                           = "False" # Toujours False askip (pas compris pq à voir)
    "ALLOWED_HOSTS"                   = "*"
    
    # Configuration Port
    "WEBSITES_PORT"                   = "8000"
  }
}

# 10. OUTPUTS
output "webapp_url" {
  value = "https://${azurerm_linux_web_app.webapp.default_hostname}"
}

output "acr_login_server" {
  value = azurerm_container_registry.acr.login_server
}

output "acr_admin_username" {
  value = azurerm_container_registry.acr.admin_username
}

output "acr_admin_password" {
  value = azurerm_container_registry.acr.admin_password
  sensitive = true
}