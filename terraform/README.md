# Compass Platform - Terraform Deployment

Este directorio contiene la configuración de Terraform para desplegar el servicio `compass-platform` en ECS.

## 🏗️ Estructura

```
terraform/
├── modules/
│   └── ecs_service/          # Módulo reutilizable para ECS service
│       ├── main.tf           # Task definition, service, autoscaling
│       ├── iam.tf            # Task execution & task roles
│       ├── variables.tf      # Input variables del módulo
│       └── outputs.tf        # Output values del módulo
└── envs/
    ├── dev/                  # Ambiente de desarrollo
    │   ├── backend.tf        # Configuración de estado remoto
    │   ├── providers.tf      # Provider AWS
    │   ├── data.tf           # Data sources (VPC, cluster, ALB, etc.)
    │   ├── main.tf           # Configuración del módulo ecs_service
    │   ├── variables.tf      # Variables del ambiente
    │   ├── terraform.tfvars  # Valores de variables
    │   ├── outputs.tf        # Outputs del ambiente
    │   └── .gitignore        # Archivos ignorados
    ├── staging/              # (Futuro) Ambiente de staging
    └── prod/                 # (Futuro) Ambiente de producción
```

## 🚀 Arquitectura

Este Terraform gestiona:
- **ECS Service**: Definición del servicio Fargate
- **ECS Task Definition**: Configuración del contenedor
- **IAM Roles**: Permisos de ejecución y runtime para la aplicación
- **Security Groups**: Reglas de red para el servicio
- **Auto Scaling**: Políticas de escalado automático (opcional)

La infraestructura base (VPC, Cluster, ALB, ECR) es gestionada por `compass-infra-tf` y referenciada mediante data sources.

## 📋 Prerequisitos

1. Infraestructura base desplegada desde `compass-infra-tf/envs/dev`
2. Imagen Docker en ECR
3. AWS credentials configuradas

## 🚀 Uso

### Inicialización

```bash
cd terraform/envs/dev
terraform init
```

### Plan

```bash
terraform plan
```

### Deploy

```bash
terraform apply
```

### Actualizar imagen

Para desplegar una nueva versión de la aplicación:

```bash
# Opción 1: Actualizar terraform.tfvars con el nuevo tag
terraform apply -var="image_tag=abc123"

# Opción 2: Desde CI/CD (recomendado)
# El workflow de GitHub Actions actualizará automáticamente
```

## 🔧 Configuración

### Variables principales

Edita `envs/dev/terraform.tfvars`:

```hcl
# Capacidad
desired_count = 2
cpu           = 512
memory        = 1024

# Environment variables
environment_variables = {
  ENVIRONMENT = "dev"
  LOG_LEVEL   = "DEBUG"
}

# Auto scaling
enable_autoscaling = true
autoscaling_max_capacity = 10
```

### Secrets

Para agregar secrets desde AWS Secrets Manager:

```hcl
secrets = {
  API_KEY = "arn:aws:secretsmanager:us-east-1:ACCOUNT:secret:compass/api-key"
}
```

## 📊 Outputs

Después del apply, obtendrás:
- `service_name`: Nombre del servicio ECS
- `task_definition_arn`: ARN de la task definition
- `image_uri`: URI completa de la imagen deployada

## 🔍 Debugging

### Ver logs

```bash
aws logs tail /ecs/compass-dev --follow
```

### Ejecutar comandos en contenedor

```bash
# Obtener task ARN
TASK_ARN=$(aws ecs list-tasks --cluster compass-dev --service-name compass-platform-dev --query 'taskArns[0]' --output text)

# Conectar
aws ecs execute-command \
  --cluster compass-dev \
  --task $TASK_ARN \
  --container compass-platform \
  --interactive \
  --command "/bin/bash"
```

## 🌍 Múltiples Ambientes

Para crear un nuevo ambiente (staging, prod):

```bash
# Copiar la estructura de dev
cp -r envs/dev envs/staging

# Actualizar archivos:
# - backend.tf: cambiar key a "compass/platform/staging/terraform.tfstate"
# - terraform.tfvars: ajustar variables para staging
# - providers.tf: verificar región si es diferente
```

## 🔄 CI/CD

Este Terraform será ejecutado automáticamente por GitHub Actions en `.github/workflows/deploy.yml`.

El flujo es:
1. Push a `main` → Build imagen → Push a ECR
2. Terraform apply con nuevo `image_tag` (commit SHA)
3. ECS actualiza el servicio con nueva task definition

## 📝 Notas

- El state se almacena en `s3://tekove-compass-tf-states-dev/compass/platform/dev/`
- Las variables sensibles deben ir en Secrets Manager, no en terraform.tfvars
- `desired_count` tiene `ignore_changes` para permitir auto scaling manual
- El módulo `ecs_service` es reutilizable para otros ambientes
