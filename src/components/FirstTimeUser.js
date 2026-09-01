import { Button } from "flowbite-react"

const posts = [
    {
      id: 1,
      title: 'Enroll in a course and get started',
      href: '#',
      description:
        'As of now, we have only one course available - "High Voltage Engineering" for you to enroll in. We are working on adding more.',
      date: 'Mar 16, 2020',
      datetime: '2020-03-16',
      category: { title: 'Step 1', href: '#' },
      buttonText: 'Enroll Now',
      buttonCTAlink: '#',
      author: {
        name: 'Michael Foster',
        role: 'Co-Founder / CTO',
        href: '#',
        imageUrl:
          '',
      },
    },
    {
        id: 2,
        title: 'Do a few experiments',
        href: '#',
        description:
          'Try an interactive lesson to get a feel for the platform. Try the features like 3D visualization and AI-based personalized learning.',
        date: 'Mar 16, 2020',
        datetime: '2020-03-16',
        category: { title: 'Step 2', href: '#' },
        buttonText: 'Try an experiment',
        buttonCTAlink: '#',
        author: {
          name: 'Michael Foster',
          role: 'Co-Founder / CTO',
          href: '#',
          imageUrl:
            '',
        },
      },
      {
        id: 3,
        title: 'Help us improve',
        href: '#',
        description:
          'Please provide feedback on the course and the platform. Your feedback is valuable to us and will help us improve the platform.',
        date: 'Mar 16, 2020',
        datetime: '2020-03-16',
        category: { title: 'Step 3', href: 'https://docs.google.com/forms/d/e/1FAIpQLSc5tkZWMMambRuszuSJ4qc5iv3iHCCUeu4Afn_LJ-mRSJsHhw/viewform?usp=sharing' },
        buttonText: 'Give feedback',
        buttonCTAlink: 'https://docs.google.com/forms/d/e/1FAIpQLSc5tkZWMMambRuszuSJ4qc5iv3iHCCUeu4Afn_LJ-mRSJsHhw/viewform?usp=sharing',
        author: {
          name: 'Michael Foster',
          role: 'Co-Founder / CTO',
          href: '#',
          imageUrl:
            '',
        },
      },
  ]
  
  export default function FirstTimeUser() {
    return (
      <div className="bg-gradient-to-tr from-amber-50 to-rose-100 dark:from-gray-600 dark:to-black py-24 sm:py-32 border-b">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="mx-auto max-w-2xl lg:mx-0">
            <h2 className="font-heading text-xl font-bold tracking-tight text-gray-700 dark:text-gray-200 sm:text-xl">How to explore Virtual Labs</h2>
            <p className="font-sans mt-2 text-base leading-8 text-gray-600 dark:text-gray-400">
              Take your learning to the next level with interactive 3D visualization and experiments.
            </p>
          </div>
          <div className="font-sans mx-auto py-4 grid max-w-2xl grid-cols-1 gap-x-8 gap-y-4 border-t border-b border-gray-400 pt-10 sm:mt-16 sm:pt-16 lg:mx-0 lg:max-w-none lg:grid-cols-3">
            {posts.map((post) => (
              <article key={post.id} className="flex max-w-xl flex-col items-start justify-between">
                <div className="flex items-center gap-x-4 text-xs dark:text-gray-200">
                  {/* <time dateTime={post.datetime} className="text-gray-500">
                    {post.date}
                  </time> */}
                  <a
                    href={post.category.href}
                    className="relative z-10 rounded-full bg-gray-50 px-3 py-1.5 font-medium text-gray-600 hover:bg-gray-100 dark:text-gray-400"
                  >
                    {post.category.title}
                  </a>
                </div>
                <div className="group relative">
                  <h3 className="mt-3 text-lg font-semibold leading-6 text-gray-900 group-hover:text-gray-600 dark:text-gray-400">
                    <a href={post.href}>
                      <span className="absolute inset-0" />
                      {post.title}
                    </a>
                  </h3>
                  <p className="mt-5 line-clamp-3 text-sm leading-6 text-gray-600 dark:text-gray-400">{post.description}</p>
                </div>
                <Button outline gradientDuoTone="redToYellow" className="mt-6 out" size="sm" rounded="md" onClick={() => window.open(post.buttonCTAlink)}>
                    {post.buttonText}
                </Button>
              </article>
            ))}
          </div>
        </div>
      </div>
    )
  }
  