import os
import pandas as pd
import matplotlib.pyplot as plt
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)
CSV_FILE = "vitalis_datos.csv"

def inicializar_csv():
    if not os.path.exists(CSV_FILE):
        data = {
            "id_paciente": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            "nombre": ["Ana Pérez", "Carlos Gómez", "María Rodríguez", "Luis Torres", "Elena Ruiz", "Jorge Díaz", "Sofía Castro", "Mateo Morales", "Lucía Rojas", "Diego Silva"],
            "edad": [28, 45, 34, 52, 29, 61, 38, 42, 25, 50],
            "ciudad": ["Bogotá", "Medellín", "Bogotá", "Cali", "Medellín", "Cali", "Bogotá", "Medellín", "Cali", "Bogotá"],
            "servicio": ["Medicina General", "Cardiología", "Nutrición", "Cardiología", "Medicina General", "Cardiología", "Nutrición", "Medicina General", "Nutrición", "Cardiología"],
            "costo_servicio": [120000, 250000, 90000, 260000, 115000, 240000, 95000, 130000, 90000, 255000],
            "satisfaccion": [5, 4, 5, 3, 4, 5, 4, 4, 5, 3]
        }
        df = pd.DataFrame(data)
        df.to_csv(CSV_FILE, index=False)

def generar_graficas():
    os.makedirs("static", exist_ok=True)
    df = pd.read_csv(CSV_FILE)

    df_servicio = df.groupby("servicio")["costo_servicio"].sum().reset_index()
    plt.figure(figsize=(7, 4))
    plt.bar(df_servicio["servicio"], df_servicio["costo_servicio"] / 1000, color="#0077b6")
    plt.title("Ingresos por Servicio (Miles COP)", fontsize=11, fontweight="bold")
    plt.xlabel("Servicio Médico")
    plt.ylabel("Ingresos (Miles COP)")
    plt.tight_layout()
    plt.savefig("static/ingresos_servicio.png")
    plt.close()

    df_ciudad = df.groupby("ciudad")["satisfaccion"].mean().reset_index()
    plt.figure(figsize=(7, 4))
    plt.bar(df_ciudad["ciudad"], df_ciudad["satisfaccion"], color="#00b4d8")
    plt.title("Satisfacción Promedio por Ciudad", fontsize=11, fontweight="bold")
    plt.xlabel("Ciudad")
    plt.ylabel("Calificación (1-5)")
    plt.ylim(0, 5)
    plt.tight_layout()
    plt.savefig("static/satisfaccion_ciudad.png")
    plt.close()

@app.route("/", methods=["GET", "POST"])
def index():
    inicializar_csv()
    if request.method == "POST":
        df = pd.read_csv(CSV_FILE)
        nuevo_registro = {
            "id_paciente": len(df) + 1,
            "nombre": request.form["nombre"],
            "edad": int(request.form["edad"]),
            "ciudad": request.form["ciudad"],
            "servicio": request.form["servicio"],
            "costo_servicio": float(request.form["costo_servicio"]),
            "satisfaccion": int(request.form["satisfaccion"])
        }
        df_nuevo = pd.DataFrame([nuevo_registro])
        df = pd.concat([df, df_nuevo], ignore_index=True)
        df.to_csv(CSV_FILE, index=False)
        generar_graficas()
        return redirect(url_for("dashboard"))
    
    return render_template("index.html")

@app.route("/dashboard")
def dashboard():
    inicializar_csv()
    generar_graficas()
    df = pd.read_csv(CSV_FILE)
    
    total_pacientes = len(df)
    ingresos_totales = df["costo_servicio"].sum()
    promedio_edad = round(df["edad"].mean(), 1)
    satisfaccion_media = round(df["satisfaccion"].mean(), 1)
    
    resumen_servicio = df.groupby("servicio").agg(
        total_atenciones=('id_paciente', 'count'),
        ingresos_totales=('costo_servicio', 'sum')
    ).reset_index().to_dict(orient="records")

    registros = df.to_dict(orient="records")
    
    return render_template(
        "resultados.html", 
        total_pacientes=total_pacientes,
        ingresos_totales=ingresos_totales,
        promedio_edad=promedio_edad,
        satisfaccion_media=satisfaccion_media,
        resumen_servicio=resumen_servicio,
        registros=registros
    )

if __name__ == "__main__":
    app.run(debug=True)