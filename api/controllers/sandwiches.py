from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from fastapi import HTTPException, status, Response, Depends
from ..models import models, schemas


def create(db: Session, sandwich: schemas.SandwichCreate):
    # Create a new instance of the Sandwich model with the provided data
    db_sandwich = models.Sandwich(
        sandwich_name=sandwich.sandwich_name,
        price=sandwich.price
    )

    # Add the newly created Sandwich object to the database session
    db.add(db_sandwich)

    try:
        # Commit the changes to the database
        db.commit()
        # Refresh the Sandwich object to ensure it reflects the current state in the database
        db.refresh(db_sandwich)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Database integrity error')
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL, detail="Error creating sandwich")

    # Return the newly created Sandwich object
    return db_sandwich


def read_all(db: Session):
    try:
        # Retrieve all rows in the Sandwich table
        return db.query(models.Sandwich).all()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error retrieving sandwiches.")


def read_one(db: Session, sandwich_id: int):
    # Retrieve a specific sandwich by its ID
    db_sandwich = db.query(models.Sandwich).filter(models.Sandwich.id == sandwich_id).first()
    if db_sandwich is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sandwich not found")
    return db_sandwich


def update(db: Session, sandwich_id: int, sandwich: schemas.SandwichUpdate):
    # Query the database for the specific sandwich to update
    db_sandwich = db.query(models.Sandwich).filter(models.Sandwich.id == sandwich_id)

    if db_sandwich.first() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sandwich not found")

    # Extract the update data from the provided 'sandwich' object
    update_data = sandwich.model_dump(exclude_unset=True)

    try:
        # Update the database record with the new data, without synchronizing the session
        db_sandwich.update(update_data, synchronize_session=False)
        # Commit the changes to the database
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Error updating sandwich')

    # Return the updated sandwich record
    return db_sandwich.first()


def delete(db: Session, sandwich_id: int):
    # Query the database for the specific sandwich to delete
    db_sandwich = db.query(models.Sandwich).filter(models.Sandwich.id == sandwich_id)

    if db_sandwich.first() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sandwich not found")

    try:
        # Delete the database record without synchronizing the session
        db_sandwich.delete(synchronize_session=False)
        # Commit the changes to the database
        db.commit()

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Error deleting sandwich')

    # Return a response with a status code indicating success (204 No Content)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
