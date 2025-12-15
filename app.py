from flask import Flask, render_template, send_file, request, session, redirect, url_for, flash
from werkzeug.utils import secure_filename
import pdfkit
import os
import uuid
import base64
import platform
import shutil

app = Flask(__name__, static_folder='Static')
app.config["UPLOAD_FOLDER"] = "static/uploads"
app.secret_key = 'admin_secret_key_123'

if platform.system() == "Windows":
    WKHTMLTOPDF_PATH = r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"
else:
    # descobrir onde está o wkhtmltopdf no Linux / Docker
    WKHTMLTOPDF_PATH = shutil.which("wkhtmltopdf")

config = pdfkit.configuration(wkhtmltopdf=WKHTMLTOPDF_PATH)

def get_image_base64(filename):
    if not filename:
        return None
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(file_path):
        with open(file_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
            return f"data:image/jpeg;base64,{encoded_string}"
    return None

# =============================================
#                PÁGINA INICIAL
# =============================================
@app.route("/")
def home():
    return render_template("index.html")

# =============================================
#                   TERMO
# =============================================
@app.route("/termo", methods=["GET", "POST"])
def termo():
    if request.method == "POST":
        registro = request.form.to_dict()

        registro_id = str(uuid.uuid4())
        registro['id'] = registro_id

        registros_termos.append(registro)
        session['registro_id'] = registro_id

        flash("Termo salvo com sucesso!", "success")
        return redirect(url_for("termo"))

    return render_template("termo.html")

# =============================================
#                  RESSALVAS
# =============================================
@app.route("/ressalvas", methods=["GET", "POST"])
def ressalvas():
    if request.method == "POST":
        registro_id = session.get("registro_id")

        if not registro_id:
            flash("Erro: Salve o Termo antes de registrar as ressalvas.", "error")
            return redirect(url_for("ressalvas"))

        registro = request.form.to_dict()
        registro["id"] = registro_id

        # Handle photo upload
        if 'foto_ressalvas' in request.files:
            file = request.files['foto_ressalvas']
            if file.filename != '':
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                registro['foto_ressalvas'] = filename

        registros_ressalvas.append(registro)

        flash("Ressalvas salvas com sucesso!", "success")
        return redirect(url_for("ressalvas"))

    return render_template("ressalvas.html")

# =============================================
#                      NPS
# =============================================
@app.route("/nps", methods=["GET", "POST"])
def nps():
    if request.method == "POST":
        registro_id = session.get("registro_id")

        if not registro_id:
            flash("Erro: Salve o Termo antes de registrar o NPS.", "error")
            return redirect(url_for("nps"))

        registro = {
            "id": registro_id,
            "nota": request.form.get("nota"),
            "comentario": request.form.get("comentario"),

            # eCSAT
            "csat0": request.form.get("csat0"),
            "csat1": request.form.get("csat1"),
            "csat2": request.form.get("csat2"),
            "csat3": request.form.get("csat3"),
            "csat4": request.form.get("csat4"),
            "csat5": request.form.get("csat5"),

            # perguntas abertas
            "aberto1": request.form.get("aberto1"),
            "aberto2": request.form.get("aberto2"),
            "aberto3": request.form.get("aberto3"),
            "aberto4": request.form.get("aberto4"),
        }

        registros_nps.append(registro)

        flash("NPS registrado com sucesso!", "success")
        return redirect(url_for("nps"))

    return render_template("nps.html")

# =============================================
#                  ADMIN
# =============================================

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if username == "admin" and password == "admin123":
            session["admin"] = True
            return redirect(url_for("admin"))

        flash("Usuário ou senha inválidos", "error")
        return redirect(url_for("login"))

    return render_template("login.html")

@app.route("/admin")
def admin():
    if "admin" not in session:
        return redirect(url_for("login"))

    return render_template(
        "admin.html",
        termos=registros_termos,
        ressalvas=registros_ressalvas,
        nps=registros_nps,
        current_project_name=current_project_name
    )

@app.route("/admin_logout")
def admin_logout():
    session.pop("admin", None)
    return redirect(url_for("login"))

# =============================================
#              DEFINIR NOME DO PROJETO
# =============================================
@app.route("/definir_projeto", methods=["POST"])
def definir_projeto():
    global current_project_name
    nome_projeto = request.form.get("nome_projeto")

    if not nome_projeto:
        flash("Preencha o nome do projeto.", "error")
        return redirect(url_for("admin"))

    current_project_name = nome_projeto

    flash("Nome do projeto salvo com sucesso!", "success")
    return redirect(url_for("admin"))

# =============================================
#        PDFs COM NOME DO PROJETO
# =============================================
@app.route("/pdf_termo/<id>")
def pdf_termo_id(id):
    registro = next((r for r in registros_termos if r["id"] == id), None)
    if not registro:
        return "Registro não encontrado", 404

    projeto = current_project_name

    html = render_template("termo_display.html", dados=registro, projeto=projeto)
    filename = f"termo_{projeto}.pdf"

    pdfkit.from_string(html, filename, configuration=config)
    return send_file(filename, as_attachment=True)

@app.route("/pdf_ressalvas/<id>")
def pdf_ressalvas_id(id):
    registro = next((r for r in registros_ressalvas if r["id"] == id), None)
    if not registro:
        return "Registro não encontrado", 404

    projeto = current_project_name
    foto_base64 = get_image_base64(registro.get('foto_ressalvas'))

    html = render_template("ressalvas_display.html", dados=registro, projeto=projeto, foto_base64=foto_base64)
    filename = f"ressalvas_{projeto}.pdf"

    pdfkit.from_string(html, filename, configuration=config)
    return send_file(filename, as_attachment=True)

@app.route("/pdf_nps/<id>")
def pdf_nps_id(id):
    registro = next((r for r in registros_nps if r["id"] == id), None)
    if not registro:
        return "Registro não encontrado", 404

    projeto = current_project_name

    html = render_template("nps_resultado.html", dados=registro, projeto=projeto)
    filename = f"nps_{projeto}.pdf"

    pdfkit.from_string(html, filename, configuration=config)
    return send_file(filename, as_attachment=True)

# =============================================
#     BANCO EM MEMÓRIA
# =============================================
registros_termos = []
registros_ressalvas = []
registros_nps = []
current_project_name = "Projeto sem nome"

if __name__ == "__main__":
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    app.run(debug=True)









