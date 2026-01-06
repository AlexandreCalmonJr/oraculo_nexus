"""
Ponto de entrada da aplicação
"""
from app import create_app

app = create_app()

if __name__ == '__main__':
    # Usar socketio.run() para suportar WebSockets
    app.socketio.run(app, debug=True, allow_unsafe_werkzeug=True)
