export interface User {
    appUserId: string;
    userName: string;
    firstName: string;
    lastName: string;
    email: string;
    createdAt: Date;
    updatedAt: Date;
    hasApprovedTermsOfUse: boolean;
    emailConfirmed: boolean;
    phoneNumber:string;
    hiredDate?: Date;
    position?: string;
    roles: string[];
}

export interface UpdateUserViewModel {
    userName: string;
    firstName: string;
    lastName: string;
    email: string;
    phoneNumber?: string;
    position?: string;
}

export interface UpdateRoleByIdViewModel {
    userId: string;
    newRole: string;
}

export interface LoginViewModel {
    userName: string;
    password: string;
}

export interface LoginResponseViewModel {
    newToken: string;
    userInfo: User; 
}



export interface MeViewModel {
    token: string;
}


export interface RegisterViewModel {
    userName: string;
    firstName: string;
    lastName: string;
    password: string;
    confirmPassword: string;
    phoneNumber?: string;
    hiredDate?: Date;
    position?: string;
    roles?: string[];
}


export interface ResetPasswordViewModel {
    userId: string;
    newPassword: string;
}



export interface UserChangePasswordViewModel {
    userName: string;
    oldPassword: string;
    newPassword: string;
    confirmNewPassword: string;
}





export interface GeneralServiceResponse {
    isSucceed: boolean;
    statusCode: number;
    message: string;
  }

  export interface GeneralServiceResponseData<T> {
    isSucceed: boolean;
    statusCode: number;
    message: string;
    data?: T;
}

  export enum UserRole {
    Admin = "Admin",
    Employee = "Employee",
    User = "User"
}
  