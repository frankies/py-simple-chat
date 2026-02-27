from flask import Flask, render_template

# simple web server to host the web UI version of Alien Invasion
app = Flask(__name__, static_folder='../static', template_folder='../templates')

@app.route('/')
def index():
    # serve the HTML which contains the canvas and JS game logic
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
