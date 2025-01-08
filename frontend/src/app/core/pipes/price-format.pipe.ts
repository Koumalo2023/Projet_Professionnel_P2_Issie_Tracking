import { Pipe, PipeTransform } from '@angular/core';

@Pipe({
  name: 'priceFormat',
  standalone: true
})
export class PriceFormatPipe implements PipeTransform {
  transform(value: number, currency: string = '€'): string {
    return `${value.toFixed(2)} ${currency}`;
  }
}
