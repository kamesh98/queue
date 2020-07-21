from queueman import app
import os

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8081))
    app.run('0.0.0.0',port=port)