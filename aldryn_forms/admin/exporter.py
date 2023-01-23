from tablib import Dataset


class Exporter(object):

    def __init__(self, queryset):
        self.queryset = queryset

    def get_dataset(self, fields):
        headers = [field.rpartition('-')[0] for field in fields]
        dataset = Dataset(headers=headers)

        for submission in self.queryset.only('data').iterator():
            row_data = []
            form_fields = [field for field in submission.get_form_data()
                           if field.field_id in fields]

            for header in fields:
                for field in form_fields:
                    if field.field_id == header:
                        row_data.append(field.value)
                        break
                else:
                    row_data.append('')

            if row_data:
                dataset.append(row_data)
        return dataset

    def get_fields_for_export(self):
        old_fields = []
        old_field_ids = []

        # A user can add fields to the form over time,
        # knowing this we use the latest form submission as a way
        # to get the latest form state.
        submissions = self.queryset.only('data').iterator()

        latest_data = next(submissions)
        latest_fields = [field for field in latest_data.get_form_data()
                         if field.label]
        latest_field_ids = [field.field_id for field in latest_fields]

        for submission in submissions:
            fields = submission.get_form_data()

            for field in fields:
                if not field.label:
                    continue

                field_id = field.field_id

                if (field_id not in old_field_ids) and (field_id not in latest_field_ids):
                    old_fields.append(field)
                    old_field_ids.append(field_id)
        return (latest_fields, old_fields)
