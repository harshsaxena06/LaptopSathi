declare module 'framer-motion' {
  import { ReactNode } from 'react';
  export const motion: {
    div: (props: any) => any;
    circle: (props: any) => any;
    rect: (props: any) => any;
    [key: string]: (props: any) => any;
  };
  export const AnimatePresence: (props: { children?: ReactNode; mode?: string; initial?: boolean }) => any;
}
