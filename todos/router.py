from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select, delete
from config.database import get_session
from todos.curd import crate_todo, update_todo, delete_todo, get_todo, get_all_todos, delete_all
from schema.schema import Create_todo, Update_todo
from auth.auth import get_current_user
from models.model import User, Todo

router = APIRouter(prefix="/todo", tags=["Todo router"])

@router.post("/create")
def create_todo(todoCreate:Create_todo, session:Session = Depends(get_session), current_user:User = Depends(get_current_user)):
    auth_user = current_user.id
    result = crate_todo(auth_user, todoCreate, session)
    return result


@router.put("/update/{id}")
def update_todo_task(id:int, updateTodo:Update_todo, session:Session=Depends(get_session), current_user:User = Depends(get_current_user)):
    todo = session.exec(select(Todo).where(Todo.id == id, Todo.user_id == current_user.id)).first()
    if not todo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No todo found")
    result = update_todo(todo.id, updateTodo,session)
    return result


@router.delete("/delete/{id}")
def delete_todo_task(id:int, session:Session=Depends(get_session), current_user:User=Depends(get_current_user)):
    todo = session.exec(select(Todo).where(Todo.id == id, Todo.user_id == current_user.id)).first()
    if not todo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No todo exsist in your id")
    return delete_todo(todo.id, session)




@router.get("/gettodo/{id}")
def get_todo_task(id:int, session:Session = Depends(get_session), current_user:User = Depends(get_current_user)):
    try:
        todo = session.exec(select(Todo).where(Todo.id == id, Todo.user_id == current_user.id)).first()
        if not todo:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authorize for the todo")
        return todo
        # return get_todo(todo.id, session)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Service unavailable")



@router.get("/alltodos")
def get_all_tasks(session:Session = Depends(get_session), current_user:User = Depends(get_current_user), page:int =1, limit:int = 5):
    all_todos = get_all_todos(session, current_user, page, limit)
    # offset = (page - 1) * limit
    # all_todos = session.exec(select(Todo).where(Todo.user_id == current_user.id).order_by(Todo.title).offset(offset).limit(limit)).all()
    return all_todos




@router.delete("/delete_all")
def delete_all_todos(session:Session = Depends(get_session), current_user:User = Depends(get_current_user)):
    result = session.exec(delete(Todo).where(Todo.user_id == current_user.id))
    session.commit()
    return {"message":"All todos Deleted suessfully"}