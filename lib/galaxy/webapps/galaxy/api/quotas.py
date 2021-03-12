"""
API operations on Quota objects.
"""
import logging

from fastapi import Path
from fastapi.param_functions import Body

from galaxy import (
    util,
    web,
)
from galaxy.managers.context import ProvidesUserContext
from galaxy.managers.quotas import QuotasManager
from galaxy.quota._schema import (
    CreateQuotaParams,
    CreateQuotaResult,
    DeleteQuotaPayload,
    QuotaDetails,
    QuotaSummaryList,
    UpdateQuotaParams,
)
from galaxy.schema.fields import EncodedDatabaseIdField
from . import (
    AdminUserRequired,
    BaseGalaxyAPIController,
    depends,
    DependsOnTrans,
    Router,
)

log = logging.getLogger(__name__)


router = Router(tags=['quotas'])


QuotaIdPathParam: EncodedDatabaseIdField = Path(
    ...,  # Required
    title="Quota ID",
    description="The encoded indentifier of the Quota."
)


@router.cbv
class FastAPIQuota:
    manager: QuotasManager = depends(QuotasManager)

    @router.get(
        '/api/quotas',
        summary="Displays a list with information of quotas that are currently active.",
        dependencies=[AdminUserRequired],
    )
    def index(
        self,
        trans: ProvidesUserContext = DependsOnTrans,
    ) -> QuotaSummaryList:
        """Displays a list with information of quotas that are currently active."""
        return self.manager.index(trans)

    @router.get(
        '/api/quotas/deleted',
        summary="Displays a list with information of quotas that have been deleted.",
        dependencies=[AdminUserRequired],
    )
    def index_deleted(
        self,
        trans: ProvidesUserContext = DependsOnTrans,
    ) -> QuotaSummaryList:
        """Displays a list with information of quotas that have been deleted."""
        return self.manager.index(trans, deleted=True)

    @router.get(
        '/api/quotas/{id}',
        summary="Displays details on a particular active quota.",
        dependencies=[AdminUserRequired],
    )
    def show(
        self,
        trans: ProvidesUserContext = DependsOnTrans,
        id: EncodedDatabaseIdField = QuotaIdPathParam
    ) -> QuotaDetails:
        """Displays details on a particular active quota."""
        return self.manager.show(trans, id)

    @router.get(
        '/api/quotas/deleted/{id}',
        summary="Displays details on a particular quota that has been deleted.",
        dependencies=[AdminUserRequired],
    )
    def show_deleted(
        self,
        trans: ProvidesUserContext = DependsOnTrans,
        id: EncodedDatabaseIdField = QuotaIdPathParam,
    ) -> QuotaDetails:
        """Displays details on a particular quota that has been deleted."""
        return self.manager.show(trans, id, deleted=True)

    @router.post(
        '/api/quotas',
        summary="Creates a new quota.",
        dependencies=[AdminUserRequired],
    )
    def create(
        self,
        payload: CreateQuotaParams,
        trans: ProvidesUserContext = DependsOnTrans,
    ) -> CreateQuotaResult:
        """Creates a new quota."""
        return self.manager.create(trans, payload)

    @router.put(
        '/api/quotas/{id}',
        summary="Updates an existing quota.",
        dependencies=[AdminUserRequired],
    )
    def update(
        self,
        payload: UpdateQuotaParams,
        id: EncodedDatabaseIdField = QuotaIdPathParam,
        trans: ProvidesUserContext = DependsOnTrans,
    ) -> str:
        """Updates an existing quota."""
        return self.manager.update(trans, id, payload)

    @router.delete(
        '/api/quotas/{id}',
        summary="Deletes an existing quota.",
        dependencies=[AdminUserRequired],
    )
    def delete(
        self,
        id: EncodedDatabaseIdField = QuotaIdPathParam,
        trans: ProvidesUserContext = DependsOnTrans,
        payload: DeleteQuotaPayload = Body(None),  # Optional
    ) -> str:
        """Deletes an existing quota."""
        return self.manager.delete(trans, id, payload)

    @router.post(
        '/api/quotas/deleted/{id}/undelete',
        summary="Restores a previously deleted quota.",
        dependencies=[AdminUserRequired],
    )
    def undelete(
        self,
        id: EncodedDatabaseIdField = QuotaIdPathParam,
        trans: ProvidesUserContext = DependsOnTrans,
    ) -> str:
        """Restores a previously deleted quota."""
        return self.manager.undelete(trans, id)


class QuotaAPIController(BaseGalaxyAPIController):

    manager: QuotasManager = depends(QuotasManager)

    @web.require_admin
    @web.expose_api
    def index(self, trans, deleted='False', **kwd):
        """
        GET /api/quotas
        GET /api/quotas/deleted
        Displays a collection (list) of quotas.
        """
        deleted = util.string_as_bool(deleted)
        return self.manager.index(trans, deleted)

    @web.require_admin
    @web.expose_api
    def show(self, trans, id, deleted='False', **kwd):
        """
        GET /api/quotas/{encoded_quota_id}
        GET /api/quotas/deleted/{encoded_quota_id}
        Displays information about a quota.
        """
        deleted = util.string_as_bool(deleted)
        return self.manager.show(trans, id, deleted)

    @web.require_admin
    @web.expose_api
    def create(self, trans, payload, **kwd):
        """
        POST /api/quotas
        Creates a new quota.
        """
        params = CreateQuotaParams(**payload)
        return self.manager.create(trans, params)

    @web.require_admin
    @web.expose_api
    def update(self, trans, id, payload, **kwd):
        """
        PUT /api/quotas/{encoded_quota_id}
        Modifies a quota.
        """
        params = UpdateQuotaParams(**payload)
        return self.manager.update(trans, id, params)

    @web.require_admin
    @web.expose_api
    def delete(self, trans, id, **kwd):
        """
        DELETE /api/quotas/{encoded_quota_id}
        Deletes a quota
        """
        # a request body is optional here
        payload = DeleteQuotaPayload(**kwd.get('payload', {}))
        return self.manager.delete(trans, id, payload)

    @web.require_admin
    @web.expose_api
    def undelete(self, trans, id, **kwd):
        """
        POST /api/quotas/deleted/{encoded_quota_id}/undelete
        Undeletes a quota
        """
        return self.manager.undelete(trans, id)
