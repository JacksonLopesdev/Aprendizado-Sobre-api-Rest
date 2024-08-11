from itertools import count
from typing import Optional
from flask import Flask, request, jsonify
from flask_pydantic_spec import FlaskPydanticSpec, Response, Request
from pydantic import BaseModel, Field
from tinydb import TinyDB, Query
from tinydb.storages import MemoryStorage

server = Flask(__name__)
spec = FlaskPydanticSpec('flask', title='Api de livros do Jackson')
spec.register(server)
database = TinyDB(storage = MemoryStorage)
contador = count()

class QueryLivro(BaseModel):
    id: Optional[int] 
    Nome_do_livro: Optional[str]
    Nome_do_autor: Optional[str]
    Data_de_lancamento: Optional[str] 
    Numero_de_paginas: Optional[int] 
    Genero: Optional[str] 
    Idioma: Optional[str] 
    Editora: Optional[str] 
    Resumo_Descricao: Optional[str] 


class Livro(BaseModel):
    id: Optional[int] = Field(default_factory=lambda: next(contador))
    Nome_do_livro: str
    Nome_do_autor: str
    Data_de_lancamento: Optional[str] = None
    Numero_de_paginas: Optional[int] = None
    Genero: Optional[str] = None
    Idioma: Optional[str] = None
    Editora: Optional[str] = None
    Resumo_Descricao: Optional[str] = None
        

class Livros(BaseModel):
    Livros: list[Livro]
    count: int


@server.get('/livros')  # rota, endpoint, recurso ...
@spec.validate(
    query=QueryLivro,
    resp=Response(HTTP_200=Livros))
   
def buscar_livros():
    query = request.context.query.dict(exclude_none=True)
    todos_os_livros = database.search(
        Query().fragment(query)
    )
    return jsonify(
        Livros(
            Livros=todos_os_livros,
            count=len(todos_os_livros)
            ).dict()
        )

@server.get('/livros/<int:id>')  # rota, endpoint, recurso ...
@spec.validate(resp=Response(HTTP_200=Livro))

def buscar_Livro(id):
    """Retorna todas as Livros da base de dados"""
    try:
        Livro = database.search(Query().id == id)[0]
        return jsonify(Livro)
    except IndexError:
        return {'message': 'Livro não encontrado !'}, 404
        


@server.post('/livros')
@spec.validate(body=Request(Livro), resp=Response(HTTP_201 = Livro))

def inserir_Livro():
   """Insere uma Livro no banco de dados"""
   body = request.context.body.dict()
   database.insert(body)
   return body

@server.put('/livros/<int:id>')
@spec.validate(
    body=Request(Livro), resp=Response(HTTP_200=Livros)
)

def altera_Livro(id):
    """Editar Livro do banco de dados"""
    Livro = Query()
    body = request.context.body.dict()
    database.update(body, Livro.id == id)
    return jsonify(body)

@server.delete('/livros/<int:id>')
@spec.validate(resp=Response(HTTP_200=Livros))

def deleta_Livro(id):
    """Deleta Livro do banco de dados"""
    Livro = Query()
    database.remove(Livro.id == id)
    return jsonify({})


server.run()