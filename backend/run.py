from almanac_backend import app, io

if __name__ == '__main__':
    # app.run(debug=True, host='0.0.0.0')
    io.run(app, debug=True, host='0.0.0.0')