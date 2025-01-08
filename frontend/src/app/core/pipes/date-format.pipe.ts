import { formatDate } from '@angular/common';
import { Pipe, PipeTransform } from '@angular/core';

@Pipe({
  name: 'dateFormat',
  standalone: true
})
export class DateFormatPipe implements PipeTransform {

  transform(value: Date | string, format: string = 'dd/MM/yyyy', locale: string = 'fr-FR'): string {
    return formatDate(value, format, locale);
  }

}
