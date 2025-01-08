import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import { CinemaReservationSummary, ReservationCount, ReservationTrend, TopMovie, WeeklyReservations } from '../models/admin-dashboard.models';


@Injectable({
  providedIn: 'root',
})
export class AdminDashboardService {
  private apiUrl = `${environment.apiUrl}/admin-dashboard`;

  constructor(private http: HttpClient) {}

  /**
   * Récupère le nombre total de réservations pour un film spécifique sur une période donnée.
   * @param movieId Identifiant du film
   * @param startDate Date de début de la période
   * @param endDate Date de fin de la période
   * @returns Observable<ReservationCount> - Nombre de réservations
   */
  getReservationsCountByMovie(movieId: string, startDate: Date, endDate: Date): Observable<ReservationCount> {
    const params = new HttpParams()
      .set('movieId', movieId)
      .set('startDate', startDate.toISOString())
      .set('endDate', endDate.toISOString());
      
    return this.http.get<ReservationCount>(`${this.apiUrl}/reservations-count`, { params });
  }

  /**
   * Récupère les films les plus réservés sur une période donnée.
   * @param startDate Date de début de la période
   * @param endDate Date de fin de la période
   * @param topN Le nombre de films à récupérer
   * @returns Observable<TopMovie[]> - Liste des films et du nombre de réservations
   */
  getTopMoviesByReservations(startDate: Date, endDate: Date, topN: number): Observable<TopMovie[]> {
    const params = new HttpParams()
      .set('startDate', startDate.toISOString())
      .set('endDate', endDate.toISOString())
      .set('topN', topN.toString());

    return this.http.get<TopMovie[]>(`${this.apiUrl}/top-movies`, { params });
  }

  /**
   * Récupère les réservations hebdomadaires pour un film spécifique.
   * @param movieId Identifiant du film
   * @returns Observable<WeeklyReservations[]> - Un dictionnaire avec la date de début de la semaine et le nombre de réservations
   */
  getWeeklyReservationsCountByMovie(movieId: string): Observable<WeeklyReservations[]> {
    const params = new HttpParams().set('movieId', movieId);
    return this.http.get<WeeklyReservations[]>(`${this.apiUrl}/weekly-reservations-count`, { params });
  }

  /**
   * Récupère la tendance des réservations pour un film donné sur une période.
   * @param movieId Identifiant du film
   * @param startDate Date de début de la période
   * @param endDate Date de fin de la période
   * @returns Observable<ReservationTrend[]> - Liste des tendances de réservation par date
   */
  getReservationTrendByMovie(movieId: string, startDate: Date, endDate: Date): Observable<ReservationTrend[]> {
    const params = new HttpParams()
      .set('movieId', movieId)
      .set('startDate', startDate.toISOString())
      .set('endDate', endDate.toISOString());

    return this.http.get<ReservationTrend[]>(`${this.apiUrl}/reservation-trend`, { params });
  }

  /**
   * Récupère un résumé des réservations par cinéma sur une période donnée.
   * @param startDate Date de début de la période
   * @param endDate Date de fin de la période
   * @returns Observable<CinemaReservationSummary[]> - Liste des cinémas avec leur total de réservations
   */
  getReservationSummaryByCinema(startDate: Date, endDate: Date): Observable<CinemaReservationSummary[]> {
    const params = new HttpParams()
      .set('startDate', startDate.toISOString())
      .set('endDate', endDate.toISOString());

    return this.http.get<CinemaReservationSummary[]>(`${this.apiUrl}/cinema-reservation-summary`, { params });
  }
}
