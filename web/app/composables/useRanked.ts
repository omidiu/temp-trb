/** Last search's ranked Offers by id, so the detail page can show the score breakdown. */
export const useRanked = () => useState<Record<number, any>>('ranked', () => ({}))
