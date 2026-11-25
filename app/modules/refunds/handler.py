from fastapi import APIRouter

from app.errors import DomainError
from app.preview import preview

router = APIRouter()


@router.get('/api/samples/{sample}/refunds')
def refunds(sample: str, event: str | None = None):
    result = preview(sample)['refunds']
    if event is None:
        return result
    for row in result:
        if row['id'] == event:
            return row
    raise DomainError('RETURN_NOT_FOUND', '找不到指定退单', 404)
