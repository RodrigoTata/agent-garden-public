# Security Checks Reference

Static-analysis security checklist for the exploration step. Start with changed files (`git diff --name-only`), then widen to adjacent modules.

Classify every finding: `🔴 CRITICAL` (exploitable), `🟡 WARNING` (potential weakness), `🔵 INFO` (defense-in-depth).

---

## Broken Access Control (Backend)

For each controller/endpoint:
- `@UseGuards(AuthGuard('jwt'), RolesGuard)` present — missing = `🔴`
- `@Roles()` matches intended audience — wrong role = `🔴`
- `@Public()` only on truly public endpoints (login, register, health)
- Resource ownership verified — user A cannot access user B's data via UUID guessing
- Bulk endpoints validate ownership for **every** item

```
// turbo
grep -rn "@Public()" src/ --include="*.ts"
```

```
// turbo
grep -rn "@Controller" src/ --include="*.ts" | head -30
```

## Broken Access Control (Frontend)

```
// turbo
grep -rn "path:" src/ --include="*.ts" -A2
```

- `canActivate` guard present for admin-only routes
- Direct URL navigation to admin routes blocked for standard users
- Unguarded admin routes = `🟡`

## Injection Vulnerabilities

**SQL Injection**:
```
// turbo
grep -rn "queryRunner.query\|\.query(" src/ --include="*.ts"
```
- Parameters use `$1, $2` placeholders, NOT string concatenation — concatenation = `🔴`
- `createQueryBuilder` uses `.setParameter()` or `:param` syntax

**XSS (Frontend)**:
```
// turbo
grep -rn "bypassSecurityTrust\|innerHTML\|\[innerHTML\]" src/ --include="*.ts"
```
- `bypassSecurityTrustHtml` or unguarded `innerHTML` = `🟡`

**NoSQL/ORM Injection**:
- TypeORM `find()` doesn't accept user-controlled `where` objects directly
- No `JSON.parse()` of user input passed to query conditions

## DTO Validation

```
// turbo
grep -rn "@Body()" src/ --include="*.ts"
```

- Parameter uses a DTO class (not `any`) — `@Body() body: any` = `🔴`
- DTO uses `class-validator` decorators — missing = `🟡`
- `ValidationPipe` applied globally or per-endpoint
- Numeric inputs have `@Min`/`@Max`, strings have `@MaxLength`

## AI Security

If AI/LLM modules exist:
- User input not concatenated into prompts — missing delimiters = `🔴`
- System instructions include anti-injection directives
- PII anonymized before sending to LLM — PII leak = `🟡`
- LLM responses sanitized before frontend rendering

## Secrets & Infrastructure

```
// turbo
grep -rn "password\|secret\|apiKey\|token\|credential" src/ --include="*.ts" -i | grep -v "node_modules\|\.spec\." | head -20
```

- No hardcoded secrets in source — hardcoded production secret = `🔴`
- `.env` in `.gitignore`
- `environment.ts` contains no secrets
- `localStorage`/`sessionStorage` not storing tokens in plain text
- GCP service accounts use least-privilege roles — `Owner`/`Editor` = `🟡`

## Dependencies

```
// turbo
npm audit --production
```

Run in both repos. Critical/High CVEs = `🔴`, Moderate = `🟡`, Low = `🔵`.

## Auth & Sessions

- JWT has reasonable `expiresIn`
- Password hashing uses `bcrypt`/`argon2` with adequate rounds
- Password reset tokens are single-use and time-limited
- Login doesn't leak whether email exists
