from flask import Flask, render_template, request, redirect
import pymysql
from datetime import datetime

app = Flask(__name__)

DB_CONFIG = {
        'host': 'localhost',
    'user': 'u325_6se6jiO2Nf',
    'password': 'PoYFSR2V5DL=!E9zg.TTRGmF',
    'database': 's325_pak_rivin',
    'cursorclass': pymysql.cursors.DictCursor
}

def get_db_connection():
    return pymysql.connect(**DB_CONFIG)

@app.route('/', methods=['GET', 'POST'])
def register():
    error_msg = None
    
    if request.method == 'POST':
        ucp_name = request.form.get('ucp_name', '').strip()
        password = request.form.get('password', '').strip()
        
        if not ucp_name or not password:
            error_msg = "Nama UCP dan Password tidak boleh kosong!"
        elif len(password) < 4:
            error_msg = "Password minimal harus 4 karakter!"
        else:
            try:
                connection = get_db_connection()
                with connection.cursor() as cursor:
                    # Cek duplikasi UCP
                    cursor.execute("SELECT ucp_name FROM ucp WHERE ucp_name = %s", (ucp_name,))
                    if cursor.fetchone():
                        error_msg = "Nama UCP ini sudah terdaftar! Gunakan nama lain."
                    else:
                        # Atur data default sesuai ketentuan awal
                        ip = ""
                        register_status = 0
                        status = 0
                        pin_code = 4096
                        reg_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        
                        # Simpan UCP beserta Password ke database
                        sql_insert = """
                            INSERT INTO ucp (ucp_name, ip, password, register, status, pin_code, reg_date)
                            VALUES (%s, %s, %s, %s, %s, %s, %s)
                        """
                        cursor.execute(sql_insert, (ucp_name, ip, password, register_status, status, pin_code, reg_date))
                        connection.commit()
                        
                        # REVISI: Berhasil daftar langsung lempar ke Web 2 (Forum di Port 7000)
                        # Kita kirim data nama UCP lewat parameter URL agar Forum tahu siapa yang login
                        return redirect(f"http://localhost:7000/?user={ucp_name}")
                        
            except Exception as e:
                error_msg = f"Terjadi kesalahan database: {str(e)}"
            finally:
                if 'connection' in locals() and connection.open:
                    connection.close()
                    
    return render_template('register.html', error_msg=error_msg)

if __name__ == '__main__':
 app.run(debug=True, host='0.0.0.0', port=9000)

