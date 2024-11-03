from sqlite3 import IntegrityError

from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from ..models import models, schemas


def create(db: Session, order_detail: schemas.OrderDetailCreate):
    # Create a new instance of the OrderDetail model with the provided data
    db_order_detail = models.OrderDetail(
        order_id=order_detail.order_id,
        sandwich_id=order_detail.sandwich_id,
        amount=order_detail.amount
    )

    # Add the newly created OrderDetail object to the database session
    db.add(db_order_detail)
    try:
        # Commit the changes to the database
        db.commit()
        # Refresh the OrderDetail object to ensure it reflects the current state in the database
        db.refresh(db_order_detail)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_Bad_Request, detail='Database integrity error')
    # Return the newly created OrderDetail object
    return db_order_detail


def read_all(db: Session):
    try:
        # Retrieve all rows in the OrderDetail table
        return db.query(models.OrderDetail).all()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL, detail="Error retrieving details.")


def read_one(db: Session, order_detail_id: int):
    # Retrieve a specific order detail by its ID
    db_order_detail = db.query(models.OrderDetail).filter(models.OrderDetail.id == order_detail_id).first()

    if db_order_detail is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order detail not found")

    return db_order_detail


def update(db: Session, order_detail_id: int, order_detail: schemas.OrderDetailUpdate):
    # Query the database for the specific order detail to update
    db_order_detail_query = db.query(models.OrderDetail).filter(models.OrderDetail.id == order_detail_id)

    if db_order_detail_query.first() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order detail not found")

    # Extract the update data from the provided 'order_detail' object
    update_data = order_detail.model_dump(exclude_unset=True)

    try:
        # Update the database record with the new data, without synchronizing the session
        db_order_detail_query.update(update_data, synchronize_session=False)

        # Commit the changes to the database
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_Bad_Request, detail='Error updating order details')

    # Return the updated order detail record
    return db_order_detail_query.first()


def delete(db: Session, order_detail_id: int):
    # Query the database for the specific order detail to delete
    db_order_detail_query = db.query(models.OrderDetail).filter(models.OrderDetail.id == order_detail_id)

    if db_order_detail_query.first() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order details not found")

    try:
        # Delete the database record without synchronizing the session
        db_order_detail_query.delete(synchronize_session=False)

        # Commit the changes to the database
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_Bad_Request, detail='Error deleting order details')

    # Return a response with a status code indicating success (204 No Content)
    return {"status": "success", "detail": "Order detail deleted"}
