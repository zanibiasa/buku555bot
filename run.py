from botDuitModule import app


if __name__ == '__main__':
    # note the threaded arg which allow
    # your app to have more than one thread
    app.run(host="0.0.0.0", port=8443, debug=True, ssl_context=('/home/zani/projek/fullc.pem',
                                                                 '/home/zani/projek/pr.pem'))
