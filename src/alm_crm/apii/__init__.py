class CompanyObjectAPIMixin(object):

    def perform_create(self, serializer, **kwargs):
        return serializer.save(owner=self.request.user, company_id=self.request.company.id, **kwargs)