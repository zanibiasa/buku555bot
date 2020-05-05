from botDuitModule import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nama_pemberi_id = db.Column(db.Integer, unique=False, nullable=False)
    nama_diberi_id = db.Column(db.Integer, unique=False, nullable=True)
    nama_diberi = db.Column(db.String(40), unique=False, nullable=True)
    hutang = db.relationship('Hutang', backref='sape', lazy=True)

class Hutang(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hutang_nama = db.Column(db.String(20), nullable=True)
    nilai_hutang = db.Column(db.Integer, nullable=True)
    dia_hutang= db.Column(db.Boolean, nullable=True)
    sape_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False) 