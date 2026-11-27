# FloripaUrbana
Guia digital com pontos turísticos para valorização regional, pois à um problema de que os moradores e visitantes nem sempre conhecem os pontos turísticos e culturais da região.

## Banco de dados

O aplicativo le as variaveis `MYSQL_HOST`, `MYSQL_PORT`, `MYSQL_USER`, `MYSQL_PASSWORD` e `MYSQL_DATABASE`. Para configurar no PowerShell antes de iniciar o app:

```powershell
$env:MYSQL_HOST = "127.0.0.1"
$env:MYSQL_USER = "root"
$env:MYSQL_PASSWORD = "SENHA_CORRETA_DO_MYSQL"
$env:MYSQL_DATABASE = "floripa_urbana"
python app.py
```

Crie o banco executando `banco_de_dados.sql` caso ele ainda nao exista.

## Administração

Após criar uma conta normalmente, conceda acesso administrativo a ela no MySQL:

```sql
USE floripa_urbana;
UPDATE usuarios SET is_admin = 1 WHERE email = 'seu-email@exemplo.com';
```

O painel fica em `/admin` e também aparece na navegação da conta administradora. O app adiciona automaticamente as colunas `is_admin` e `banido` em bancos existentes; instalações novas também as recebem por `banco_de_dados.sql`. Administradores podem cadastrar e excluir pontos, remover avaliações e comentários, e banir ou desbanir contas. Contas banidas não conseguem entrar nem enviar avaliações.
