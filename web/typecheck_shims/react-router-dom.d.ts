declare module 'react-router-dom' {
  import { ReactNode } from 'react';
  export const BrowserRouter: (props: { children?: ReactNode }) => any;
  export const Routes: (props: { children?: ReactNode }) => any;
  export const Route: (props: { path?: string; element?: ReactNode; children?: ReactNode }) => any;
  export const Link: (props: { to: string; children?: ReactNode; [key: string]: any }) => any;
  export const Navigate: (props: { to: string; replace?: boolean; state?: any }) => any;
  export const Outlet: (props?: any) => any;
  export function useNavigate(): (path: string, opts?: any) => void;
  export function useLocation(): { pathname: string; state?: any; [key: string]: any };
  export function useSearchParams(): [{ get(key: string): string | null }, (params: any) => void];
  export function useParams<T = Record<string, string>>(): T;
}
