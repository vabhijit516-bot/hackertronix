# Contributing to NexDev

Thank you for your interest in contributing to **NexDev**! We welcome contributions to make this full-stack platform even more robust and developer-friendly.

---

## 📜 Code of Conduct

By participating in this project, you agree to uphold a welcoming, respectful, and inclusive environment for everyone.

---

## 🛠️ Development Workflow

1. **Fork the Repository**:
   Click the "Fork" button at the top right of the GitHub repository.

2. **Clone your fork**:
   ```bash
   git clone https://github.com/<your-username>/hackertronix.git
   cd hackertronix
   ```

3. **Create a descriptive feature branch**:
   ```bash
   git checkout -b feature/jwt-token-refresh
   ```

4. **Install dependencies**:
   ```bash
   # In server/
   cd server && npm install

   # In client/
   cd ../client && npm install
   ```

5. **Make your changes**:
   - Write clean, type-safe TypeScript code.
   - Follow modular design principles.
   - Add unit tests for new service logic.

6. **Verify code quality**:
   ```bash
   # Run tests and type checks
   npm test
   npm run build
   ```

7. **Commit using Conventional Commits**:
   - `feat: add real-time latency monitoring chart`
   - `fix: correct rate-limiter header casing`
   - `docs: update API documentation with new endpoints`

8. **Submit a Pull Request**:
   Push to your fork and submit a PR against `main`. Provide a clear summary of your changes in the PR template.

---

## 📬 Reporting Bugs & Feature Requests

- Use GitHub Issues to file bug reports or feature proposals.
- Include reproduction steps, environment details, and expected behavior.
