declare module 'react' {
  export type ReactNode = any;
  export type FormEvent<T = Element> = { preventDefault(): void; target: T; currentTarget: T };
  export type ChangeEvent<T = Element> = { target: T & { value: string; checked?: boolean } };
  export type MouseEvent<T = Element> = any;
  export type CSSProperties = Record<string, any>;
  export interface SVGProps<T> {
    [key: string]: any;
  }
  export interface HTMLAttributes<T> {
    [key: string]: any;
  }

  export function useState<S>(initial: S | (() => S)): [S, (value: S | ((prev: S) => S)) => void];
  export function useEffect(effect: () => void | (() => void), deps?: any[]): void;
  export function useCallback<T extends (...args: any[]) => any>(fn: T, deps: any[]): T;
  export function useMemo<T>(fn: () => T, deps: any[]): T;
  export function useContext<T>(context: any): T;
  export function useRef<T>(initial: T | null): { current: T | null };

  export function createContext<T>(defaultValue: T | undefined): any;

  export interface ReactElement { [key: string]: any }
  export type FC<P = {}> = (props: P & { children?: ReactNode }) => ReactElement | null;
  export type PropsWithChildren<P = {}> = P & { children?: ReactNode };

  export const StrictMode: any;
  export const Fragment: any;

  const React: any;
  export default React;
}

declare module 'react/jsx-runtime' {
  export const jsx: any;
  export const jsxs: any;
  export const Fragment: any;
}

declare namespace JSX {
  interface IntrinsicElements {
    [elemName: string]: any;
  }
  interface Element {
    [key: string]: any;
  }
}
