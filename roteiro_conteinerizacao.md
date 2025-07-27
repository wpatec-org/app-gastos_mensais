# 🐳 Roteiro de Conteinerização - App Gastos Mensais

Este guia descreve o processo para construir, testar, publicar e executar sua aplicação Dockerizada localmente e em uma VM Linux utilizando Docker Hub e Docker Compose.

---

## 1 – Construir a Imagem Docker

Posicione-se na mesma pasta onde estão seus arquivos e o `Dockerfile`.

```bash
# Construção simples
docker build -t nome_image .

# Com cache desabilitado
docker build --no-cache -t app-gastos_mensais .
```

---

### 1.1 – Publicar Imagem no Docker Hub

#### ✅ Login no Docker Hub
```bash
docker login
```

#### ✅ Criar repositório no Docker Hub  
Exemplo: `app-gastos_mensais`

#### ✅ Construir imagem com nome do Docker Hub
```bash
docker build -t <login_docker_hub>/nome_da_imagem .
# Exemplo:
docker build -t cloudwpa22/app-gastos_mensais:v1 .
```

#### ✅ Enviar imagem para o Docker Hub
```bash
docker push cloudwpa22/app-gastos_mensais:v1
```

#### ✅ Criar versão atualizada da imagem
```bash
docker build -t cloudwpa22/app-gastos_mensais:v2 .
docker push cloudwpa22/app-gastos_mensais:v2
```

---

## 2 – Testar a Imagem Localmente (Opcional, mas Recomendado)

```bash
# Usando imagem local
docker run -p 5000:5000 app-gastos_mensais

# Usando imagem do Docker Hub
docker run -p 5000:5000 cloudwpa22/app-gastos_mensais:v1
```

---

## 3 – Executar na VM Linux com Docker Compose

### 📦 Volume Nomeado (recomendado)
Adicione no `docker-compose.yml`:
```yaml
volumes:
  - relatorios_data:/app/relatorios
```

### 📁 Preparar volume local
```bash
mkdir -p ./relatorios_data && sudo chown -R 1000:1000 ./relatorios_data
ls -ld ./relatorios_data
# Esperado: drwxr-xr-x 2 usuario 1000 ...
```

### 🚀 Executar com Docker Compose
```bash
# Baixar o docker-compose.yml do repositório
# Em seguida, execute:
docker-compose pull           # Puxa a imagem do Docker Hub
docker-compose up -d          # Inicia o container em background
# Ou:
docker-compose pull && docker-compose up -d
```

### 🧪 Verificações
```bash
docker-compose ps            # Verifica status dos containers
docker-compose logs -f       # Logs em tempo real
```

### 📂 Gerenciamento de Volumes
```bash
docker volume inspect app-gastos_mensais_relatorios_data
```

