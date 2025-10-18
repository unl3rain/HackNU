export type Vacancy = {
  id: number
  title: string
  city: string
  description: string
  min_experience_years: number
  employment_type: string
  skills: string[]
}

export const mockVacancies: Vacancy[] = [
  {
    id: 1,
    title: 'Frontend Developer (React)',
    city: 'Алматы',
    description:
      'Мы ищем React-разработчика для разработки виджетов и SPA. Требования: React, TypeScript, UI-библиотеки.',
    min_experience_years: 2,
    employment_type: 'full-time',
    skills: ['React', 'TypeScript', 'HTML', 'CSS'],
  },
  {
    id: 2,
    title: 'Data Analyst',
    city: 'Астана',
    description:
      'Аналитик данных: SQL, Python, визуализация. Опыт 1+ года, знание статистики приветствуется.',
    min_experience_years: 1,
    employment_type: 'full-time',
    skills: ['SQL', 'Python', 'Tableau'],
  },
]

export function getVacancies() {
  return Promise.resolve(mockVacancies)
}

export function getVacancy(id: number) {
  return Promise.resolve(mockVacancies.find((v) => v.id === id)!)
}
