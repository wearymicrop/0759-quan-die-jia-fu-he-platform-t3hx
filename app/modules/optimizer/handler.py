from fastapi import APIRouter

from app.errors import DomainError
from app.preview import preview

router = APIRouter()


@router.get('/api/samples/{sample}/optimizer')
def optimizer(sample: str, receipt: str | None = None):
    result = preview(sample)['optimizer']
    if receipt is None:
        return result
    for row in result:
        if row['id'] == receipt:
            return row
    raise DomainError('RECEIPT_NOT_FOUND', '找不到指定小票', 404)
