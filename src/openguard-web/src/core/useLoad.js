import { useCallback, useEffect, useRef, useState } from 'react';
import { errorText } from './api-client';

/** Tải dữ liệu bất đồng bộ: { data, error, loading, reload }. */
export default function useLoad(fn, deps) {
  const [state, setState] = useState({ data: null, error: '', loading: true });
  const fnRef = useRef(fn);
  fnRef.current = fn; // eslint-disable-line react-hooks/refs
  const key = JSON.stringify(deps);
  const run = useCallback(async () => {
    try {
      const data = await fnRef.current();
      setState({ data, error: '', loading: false });
    } catch (e) {
      setState({ data: null, error: errorText(e), loading: false });
    }
  }, [key]); // eslint-disable-line react-hooks/exhaustive-deps
  useEffect(() => { run(); }, [run]);
  return { ...state, reload: run };
}
