# The Art of Loving Yourself — Ebook Lead Magnet

This is a simple Streamlit website. A visitor enters their details before the ebook download appears. The details are saved in Supabase. A password-protected administrator page shows the leads.

You do not need Node.js, npm, Docker, or GitHub Actions.

## Project files

- `app.py` — the public form and ebook download
- `pages/1_Admin_Dashboard.py` — the private administrator dashboard
- `supabase_schema.sql` — creates the Supabase table
- `requirements.txt` — Python packages used by Streamlit
- `.streamlit/secrets.toml.example` — empty example of the required secrets
- `assets/the-art-of-loving-yourself.pdf` — your ebook PDF (you add this file)

## 1. Create a Supabase project

1. Go to [supabase.com](https://supabase.com/).
2. Create an account or sign in.
3. Click **New project**.
4. Choose your organization.
5. Enter a project name.
6. Create a strong database password and save it somewhere safe.
7. Choose a region close to your visitors.
8. Click **Create new project**.
9. Wait until the project is ready.

## 2. Create the leads table

1. Open your Supabase project.
2. Click **SQL Editor** in the left menu.
3. Click **New query**.
4. Open `supabase_schema.sql` from this project.
5. Copy all its text into the Supabase SQL Editor.
6. Click **Run**.
7. You should see a success message.

The SQL file creates an empty `leads` table. It does not add dummy leads. Row Level Security is enabled, and browser roles cannot read or write the table.

## 3. Find the Supabase project URL

1. In Supabase, click **Project Settings** (the gear icon).
2. Open **API**. In some Supabase layouts, this is called **Data API**.
3. Find **Project URL**.
4. Copy it. It looks similar to `https://abcdefgh.supabase.co`.

You will add this later as `SUPABASE_URL`.

## 4. Find the Supabase service-role key

The service-role key is a private server password. Never put it in `app.py`, a screenshot, or a public repository.

1. In Supabase, open **Project Settings**.
2. Open **API** or **API Keys**.
3. Find the **service_role** key under legacy keys, or the server-side **secret** key if Supabase shows the newer key format.
4. Click to reveal and copy the key.
5. Keep it private.

You will add it later as `SUPABASE_SERVICE_ROLE_KEY`. Do not use the public `anon` or publishable key for this app.

## 5. Add the ebook PDF

1. Find the `assets` folder in this project.
2. Add your finished ebook PDF to that folder.
3. Name it exactly `the-art-of-loving-yourself.pdf`.
4. Check that the full project path is `assets/the-art-of-loving-yourself.pdf`.

The PDF is read by the Python app. The public page does not show a direct ebook URL.

## 6. Test on your own computer (optional)

You need Python 3.10 or newer.

1. Open a terminal inside the project folder.
2. Create a virtual environment:

   ```bash
   python3 -m venv .venv
   ```

3. Activate it on macOS or Linux:

   ```bash
   source .venv/bin/activate
   ```

   On Windows PowerShell, use:

   ```powershell
   .venv\Scripts\Activate.ps1
   ```

4. Install the Python packages:

   ```bash
   pip install -r requirements.txt
   ```

5. Copy `.streamlit/secrets.toml.example` and name the copy `.streamlit/secrets.toml`.
6. Add your real values to the new file:

   ```toml
   SUPABASE_URL = "your-project-url"
   SUPABASE_SERVICE_ROLE_KEY = "your-private-service-role-key"
   ADMIN_USERNAME = "choose-an-admin-username"
   ADMIN_PASSWORD = "choose-a-long-strong-password"
   ```

7. Start the app:

   ```bash
   streamlit run app.py
   ```

8. Open the local address shown in the terminal, usually `http://localhost:8501`.

The real `.streamlit/secrets.toml` file is ignored by Git. Never remove it from `.gitignore`.

## 7. Upload to a private GitHub repository

1. Sign in at [github.com](https://github.com/).
2. Click **New repository**.
3. Enter a repository name, such as `loving-yourself-ebook`.
4. Select **Private**.
5. Create the repository.
6. Follow GitHub's instructions to upload or push this project folder.
7. Make sure these files are included: `app.py`, `pages/1_Admin_Dashboard.py`, `requirements.txt`, `supabase_schema.sql`, `README.md`, `.gitignore`, `.streamlit/secrets.toml.example`, and the ebook PDF.
8. Make sure `.streamlit/secrets.toml` is **not** included.

Because the repository contains the ebook, keep the repository private. Streamlit Community Cloud must be allowed to access this private repository.

## 8. Connect GitHub to Streamlit Community Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io/).
2. Sign in using GitHub.
3. Give Streamlit permission to see the private repository. GitHub may ask you to choose which repositories Streamlit can access.
4. In Streamlit Community Cloud, click **Create app** or **New app**.
5. Select your private GitHub repository.
6. Select the branch that contains the project, usually `main`.
7. For **Main file path**, enter `app.py`.

## 9. Add secrets in Advanced Settings

Before deploying, open **Advanced settings** in the Streamlit deployment screen. Paste the following and replace every value with your real value:

```toml
SUPABASE_URL = "your-project-url"
SUPABASE_SERVICE_ROLE_KEY = "your-private-service-role-key"
ADMIN_USERNAME = "your-admin-username"
ADMIN_PASSWORD = "your-long-strong-password"
```

Do not add these values to GitHub. Streamlit stores them separately from your code.

## 10. Deploy the application

1. Check that the repository, branch, and `app.py` path are correct.
2. Check that all four secrets are in Advanced Settings.
3. Click **Deploy**.
4. Wait while Streamlit installs the three Python packages from `requirements.txt`.
5. The public form will open when deployment finishes.

## 11. Find the public website URL

After deployment, the address in your browser is the public website URL. It usually looks like:

`https://your-app-name.streamlit.app`

Copy this address and share it with visitors. Test the form once yourself. Then confirm that the new lead appears in Supabase and in the dashboard.

## 12. Open the administrator dashboard

1. Open the deployed app.
2. Open the Streamlit page menu or sidebar.
3. Select **Admin Dashboard**.
4. Enter the `ADMIN_USERNAME` and `ADMIN_PASSWORD` values you put in Streamlit Secrets.

The dashboard includes lead totals, date and status filters, name and email search, sorting, CSV export, refresh, logout, and archive. Archiving keeps the lead in Supabase. It never permanently deletes the lead.

Dashboard dates and metrics use UTC. This makes the results consistent for visitors and administrators in different countries.

## 13. Update the ebook later

1. Prepare the new PDF.
2. Name it `the-art-of-loving-yourself.pdf`.
3. Replace the old file in the `assets` folder in your private GitHub repository.
4. Commit the change to the branch used by Streamlit.
5. Streamlit normally redeploys the app automatically. If it does not, open the app in Streamlit Community Cloud and choose **Reboot** or **Redeploy**.

Keep the same file name. If you change the file name, you must also change `EBOOK_PATH` near the top of `app.py`.

## 14. Common problems

### The app says the secrets are not configured

Open the app settings in Streamlit Community Cloud. Check the **Secrets** section. Make sure all four names are spelled exactly as shown in this README. TOML values must be inside quotation marks. Save the secrets and reboot the app.

### The form says it could not save the details

- Check that `supabase_schema.sql` ran successfully.
- Check that the table is named `leads`.
- Check `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY` in Streamlit Secrets.
- Make sure you copied the private service-role/secret key, not the public anon/publishable key.
- Do not paste extra spaces before or after a secret.

The website intentionally hides technical database messages from visitors.

### The ebook is unavailable

Check that the PDF is committed to the private GitHub repository at exactly:

`assets/the-art-of-loving-yourself.pdf`

File names use lowercase letters and hyphens. They are case-sensitive on Streamlit.

### The administrator login does not work

- Use the exact username and password from Streamlit Secrets.
- Passwords are case-sensitive.
- If you change a secret, save it and reboot the app.

### The app does not appear in Streamlit

- Check that **Main file path** is `app.py`.
- Check that `requirements.txt` is in the top folder of the repository.
- Check that Streamlit has permission to access the private GitHub repository.
- Open **Manage app** and read the deployment log. Do not share a log if it contains private information.

### A Python package fails to install

Check that `requirements.txt` contains only:

```text
streamlit
supabase
pandas
```

Then reboot the app.

## Security reminders

- Keep the GitHub repository private because it contains the ebook.
- Never commit `.streamlit/secrets.toml`.
- Never share the service-role key or administrator password.
- Use a long, unique administrator password.
- If a secret is accidentally shared, replace it in Supabase or Streamlit immediately.
