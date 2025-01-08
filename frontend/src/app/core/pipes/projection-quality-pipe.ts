import { Pipe, PipeTransform } from '@angular/core';
import { ProjectionQuality } from '../models/cinema.model';

@Pipe({
  name: 'projectionQuality',
  standalone: true
})
export class ProjectionQualityPipe implements PipeTransform {

  transform(value: string): string {
    switch(value) {
      case ProjectionQuality.FourDX:
        return 'FourDX';
      case ProjectionQuality.ThreeD:
        return '3D';
      case ProjectionQuality.IMAX:
        return 'IMAX';
      case ProjectionQuality.FourK:
        return '4K';
      case ProjectionQuality.Standard2D:
        return 'Standard 2D';
      case ProjectionQuality.DolbyCinema:
        return 'Dolby Cinema';
      default:
        return '4K';
    }
  }

}
