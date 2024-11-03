from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from fastapi import HTTPException, status, Response
from ..models import models, schemas
from ..models.schemas import Resource, ResourceCreate, ResourceUpdate


def create(db: Session, resource: schemas.ResourceCreate):
    # Create a new instance of the Resource model with the provided data
    db_resource = models.Resource(
        item=resource.item,
        amount=resource.amount
    )

    # Add the newly created Resource object to the database session
    db.add(db_resource)

    try:
        # Commit the changes to the database
        db.commit()

        # Refresh the Resource object to ensure it reflects the current state in the database
        db.refresh(db_resource)

    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail='Database integrity error')
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail="Error creating resource")

    # Return the newly created Resource object
    return db_resource


def read_all(db: Session):
    try:
        # Retrieve all rows in the Resource table
        return db.query(models.Resource).all()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail="Error retrieving resources.")


def read_one(db: Session, resource_id: int):
    # Retrieve a specific resource by its ID
    db_resource = db.query(models.Resource).filter(models.Resource.id == resource_id).first()
    if db_resource is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resource not found")
    return db_resource


def update(db: Session, resource_id: int, resource: schemas.ResourceUpdate):
    # Query the database for the specific resource to update
    db_resource_query = db.query(models.Resource).filter(models.Resource.id == resource_id)

    if db_resource_query.first() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resource not found")

    # Extract the update data from the provided 'resource' object
    update_data = resource.model_dump(exclude_unset=True)

    try:
        # Update the database record with the new data, without synchronizing the session
        db_resource_query.update(update_data, synchronize_session=False)
        # Commit the changes to the database
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Error updating resource",)

    # Return the updated resource record
    return db_resource_query.first()


def delete(db: Session, resource_id: int):
    # Query the database for the specific resource to delete
    db_resource_query = db.query(models.Resource).filter(models.Resource.id == resource_id)

    if db_resource_query.first() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resource not found")

    try:
        # Delete the database record without synchronizing the session
        db_resource_query.delete(synchronize_session=False)
        # Commit the changes to the database
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Error deleting resource",)

    # Return a response with a status code indicating success (204 No Content)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
