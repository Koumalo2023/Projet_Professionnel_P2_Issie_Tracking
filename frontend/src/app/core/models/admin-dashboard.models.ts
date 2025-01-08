// Modèles pour les réponses (à adapter selon vos DTO)
export interface GeneralServiceResponse<T> {
    isSucceed: boolean;
    statusCode: number;
    message: string;
    data?: T;
}

export interface ReservationCount {
    count: number;
}

export interface TopMovie {
    movieId: string;
    reservationCount: number;
}

export interface WeeklyReservations {
    weekStartDate: string; // ou Date
    reservationCount: number;
}

export interface ReservationTrend {
    date: string; // ou Date
    count: number;
}

export interface CinemaReservationSummary {
    cinemaId: string;
    reservationCount: number;
}