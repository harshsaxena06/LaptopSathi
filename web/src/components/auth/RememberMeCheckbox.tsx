import React from 'react';
import { CheckIcon } from '../Icons';

interface Props {
  checked: boolean;
  onChange: (checked: boolean) => void;
}

export function RememberMeCheckbox({ checked, onChange }: Props) {
  return (
    <label className="remember-row" htmlFor="remember-me">
      <span className="checkbox-visual">
        <input
          id="remember-me"
          type="checkbox"
          checked={checked}
          onChange={(e) => onChange(e.target.checked)}
        />
        <span className="checkbox-box" aria-hidden="true">
          <CheckIcon width={11} height={11} />
        </span>
      </span>
      Remember me
    </label>
  );
}
