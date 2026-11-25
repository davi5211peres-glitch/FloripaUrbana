# FloripaUrbana
Guia digital com pontos turísticos para valorização regional, pois à um problema de que os moradores e visitantes nem sempre conhecem os pontos turísticos e culturais da região.

## Administração

Após criar uma conta normalmente, conceda acesso administrativo a ela no MySQL:

```sql
USE floripa_urbana;
UPDATE usuarios SET is_admin = 1 WHERE email = 'seu-email@exemplo.com';
```

O painel fica em `/admin` e também aparece na navegação da conta administradora. O app adiciona automaticamente as colunas `is_admin` e `banido` em bancos existentes; instalações novas também as recebem por `banco_de_dados.sql`. Administradores podem cadastrar e excluir pontos, remover avaliações e comentários, e banir ou desbanir contas. Contas banidas não conseguem entrar nem enviar avaliações.
