# Manual para Leigos: Clonar um Repositório no WSL e Abrir no VS Code

## 1. Abrir o WSL (Ubuntu)

No Windows:

1. Pressione a tecla **Windows**.
2. Digite:

```text
Ubuntu
```

3. Abra o aplicativo **Ubuntu**.

Você verá algo parecido com:

```bash
anton@Antonio-PC:~$
```

---

## 2. Ir para a pasta onde os projetos ficarão armazenados

Caso a pasta ainda não exista:

```bash
mkdir -p ~/GitHub
```

Entre nela:

```bash
cd ~/GitHub
```

Verifique onde você está:

```bash
pwd
```

Resultado esperado:

```text
/home/anton/GitHub
```

---

## 3. Clonar o repositório

Copie a URL do repositório no GitHub.

Exemplo:

```text
https://github.com/usuario/projeto.git
```

Execute:

```bash
git clone https://github.com/usuario/projeto.git
```

Exemplo real:

```bash
git clone https://github.com/usuario/antenas__projeto-LoRa.git
```

Ao finalizar, aparecerá uma nova pasta:

```text
antenas__projeto-LoRa
```

---

## 4. Entrar na pasta do projeto

```bash
cd antenas__projeto-LoRa
```

Verifique:

```bash
pwd
```

Resultado esperado:

```text
/home/anton/GitHub/antenas__projeto-LoRa
```

---

## 5. Abrir o projeto no VS Code do Windows

Com o terminal dentro da pasta do projeto:

```bash
code .
```

O VS Code será aberto automaticamente.

Observe o canto inferior esquerdo do VS Code.

Deve aparecer algo semelhante a:

```text
WSL: Ubuntu
```

Isso significa que o VS Code do Windows está conectado ao Linux corretamente.

---

## 6. Se o comando "code" não funcionar

Teste:

```bash
code --version
```

Se aparecer erro, instale:

1. VS Code no Windows.
2. Extensão "WSL" da Microsoft.

Depois feche e abra novamente o Ubuntu.

Teste novamente:

```bash
code .
```

---

## 7. Verificar se o repositório foi clonado corretamente

Liste os arquivos:

```bash
ls
```

ou

```bash
ls -la
```

Você deverá ver os arquivos do projeto.

---

## 8. Fluxo diário de trabalho

Sempre que for trabalhar no projeto:

```bash
cd ~/GitHub/antenas__projeto-LoRa
code .
```

Pronto. O VS Code abrirá diretamente no projeto.

---

## 9. Comandos úteis

Entrar na pasta do projeto:

```bash
cd ~/GitHub/antenas__projeto-LoRa
```

Atualizar o projeto:

```bash
git pull
```

Ver alterações:

```bash
git status
```

Abrir VS Code:

```bash
code .
```

Ver caminho atual:

```bash
pwd
```

Listar arquivos:

```bash
ls -la
```
