export default function DigitRoll({value='0.00',className=''}){
 return <span className={`digit-roll money ${className}`} aria-label={String(value)}>{String(value).split('').map((c,i)=><span key={i+c} className="dr" style={{animationDelay:`${i*40}ms`}}>{c}</span>)}</span>;}
