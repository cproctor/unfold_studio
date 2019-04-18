from django.http import HttpResponse
import csv

# From https://godjango.com/blog/download-csv-files-via-csvresponemixin/
class CSVResponseMixin(object):
    csv_filename = 'csvfile.csv'

    def get_csv_filename(self):
        return self.csv_filename

    def render_to_csv(self, data, dicts=False):
        response = HttpResponse(content_type='text/csv')
        cd = 'attachment; filename="{0}"'.format(self.get_csv_filename())
        response['Content-Disposition'] = cd

        if dicts:
            writer = csv.DictWriter(response, data[0].keys())
            writer.writeheader()
            writer.writerows(data)
        else:
            writer = csv.writer(response)
            for row in data:
                writer.writerow(row)

        return response

