from fastapi import HTTPException, status
from sqlmodel import select, Session, delete
from models.model import Todo
from schema.schema import Create_todo, Update_todo
from datetime import datetime, timezone
from models.model import User

def crate_todo(id:int, todo:Create_todo, session:Session):
    try:    
        new_todo = Todo(title=todo.title, status=todo.status, user_id=id)
        session.add(new_todo)
        session.commit()
        session.refresh(new_todo)
        print(new_todo)
        return {"message": "Task added sucessfully", "todo": new_todo}
        
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e))





def update_todo(id: int, updateTodo: Update_todo, session: Session):
    try:
        existing_todo = session.get(Todo, id)

        if not existing_todo:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No todo found on this Id")

        modified_todo = updateTodo.model_dump(exclude_unset=True)

        for k, v in modified_todo.items():
            setattr(existing_todo, k, v)

        existing_todo.updatedat = datetime.now(timezone.utc)

        session.add(existing_todo)
        session.commit()
        session.refresh(existing_todo)

        return {"message": "Todo updated successfully", "updated_todo": existing_todo }

    except HTTPException as err:
        raise err



def delete_todo(id:int,session:Session):
    try:
        deleteTodo = session.get(Todo, id)

        if not deleteTodo:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No todo found on this ID")
        
        session.delete(deleteTodo)
        session.commit()
    
        return {"message":f"Todo deleted sucessfully from this ID {id}"}
    

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"{e}")
    


def get_todo(id:int, session:Session):
    try:
        todo = session.get(Todo, id)

        if not todo:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")
        
        return todo

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"{e}")
    

# def get_all_todo(session:Session):
#     try:
#         all_tasks = session.exec(select(Todo)).all()

#         if not all_tasks:
#             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No todos Found")

#         return all_tasks

#     except Exception as e:
#         raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"{e}")
    

def delete_all(session:Session):
    todos = session.exec(select(Todo)).all()
    print(todos)
    try:
        if not todos:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No Todos Found")
        
        for todo in todos:
            session.delete(todo)

        session.commit()

        return {"message": "Todos deleted sucessfully"}

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e))

def get_all_todos(session: Session, current_user:User, page:int, limit:int):
    offset = (page - 1) * limit
    all_todos = session.exec(select(Todo).where(Todo.user_id == current_user.id).order_by(Todo.title).offset(offset).limit(limit)).all()
    return all_todos